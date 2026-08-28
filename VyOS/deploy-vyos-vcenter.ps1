<#!
.SYNOPSIS
Deploys the locally built VyOS Router OVA to vCenter.

.DESCRIPTION
Defaults target vcenter.example.com, datacenter Datacenter, and cluster Cluster.
When omitted, the datastore and WAN/LAN port groups are selected interactively.
An optional config.boot file is installed automatically on first boot.
#>
[CmdletBinding()]
param(
    [string]$VCenter = 'vcenter.example.com',
    [string]$Datacenter = 'Datacenter',
    [string]$Cluster = 'Cluster',
    [string]$VmName = 'vyos-router',
    [string]$OvaPath,
    [string]$Datastore = 'datastore1',
    [string]$WanPortGroup = 'VyOS-WAN',
    [string]$LanPortGroup = 'VyOS-LAN',
    [string]$Folder,
    [ValidateRange(1, 128)]
    [int]$CpuCount = 2,
    [ValidateRange(4, 1024)]
    [int]$MemoryGB = 4,
    [string]$VyOSConfigFile,
    [PSCredential]$VyOSCredential,
    [switch]$NoPowerOn,
    [string]$SettingsPath,
    [string]$CredentialFile
)

$ErrorActionPreference = 'Stop'
if (-not $SettingsPath) { $SettingsPath = Join-Path $PSScriptRoot 'deploy-vyos-vcenter.settings.json' }
if (-not $CredentialFile) { $CredentialFile = Join-Path $PSScriptRoot 'vcenter-credential.clixml' }

# Reuse non-secret choices from a prior successful deployment. Explicit command
# line parameters always take precedence over saved values.
if (Test-Path -LiteralPath $SettingsPath) {
    try {
        $savedSettings = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json
        foreach ($settingName in 'VCenter', 'Datacenter', 'Cluster', 'VmName', 'OvaPath', 'Datastore', 'WanPortGroup', 'LanPortGroup', 'Folder', 'CpuCount', 'MemoryGB', 'VyOSConfigFile') {
            if (-not $PSBoundParameters.ContainsKey($settingName) -and $null -ne $savedSettings.$settingName -and "$($savedSettings.$settingName)".Length -gt 0) {
                Set-Variable -Name $settingName -Value $savedSettings.$settingName -Scope Script
            }
        }
        Write-Host "Loaded saved deployment settings from $SettingsPath"
    }
    catch {
        Write-Warning "Unable to read saved settings from $SettingsPath. Using the script defaults. $($_.Exception.Message)"
    }
}
if (-not $OvaPath) { $OvaPath = Join-Path $PSScriptRoot 'dist\VyOS-Router.ova' }
if (-not $VyOSConfigFile) {
    $defaultConfigFile = Join-Path $PSScriptRoot 'vyos-router.config.boot'
    if (Test-Path -LiteralPath $defaultConfigFile) { $VyOSConfigFile = $defaultConfigFile }
}

if (-not (Get-Module -ListAvailable -Name VMware.VimAutomation.Core)) {
    throw 'VMware.PowerCLI is required. Install it with: Install-Module VMware.PowerCLI -Scope CurrentUser'
}
if (-not (Test-Path -LiteralPath $OvaPath)) {
    throw "OVA not found: $OvaPath"
}
if ($VyOSConfigFile -and -not (Test-Path -LiteralPath $VyOSConfigFile -PathType Leaf)) {
    throw "VyOS configuration file not found: $VyOSConfigFile"
}
if ($VyOSConfigFile) {
    $configBytes = [System.IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $VyOSConfigFile).Path)
    if ($configBytes.Length -eq 0) { throw "VyOS configuration file is empty: $VyOSConfigFile" }
    $vyosConfigPayload = [Convert]::ToBase64String($configBytes)
}

Import-Module VMware.VimAutomation.Core -ErrorAction Stop
if (Test-Path -LiteralPath $CredentialFile) {
    $credential = Import-Clixml -LiteralPath $CredentialFile
    if ($credential -isnot [pscredential]) { throw "Credential file is not a PSCredential: $CredentialFile" }
    Write-Host "Using the encrypted vCenter credential file: $CredentialFile"
}
else {
    $credential = Get-Credential -Message "Credentials for $VCenter"
}
$viConnection = Connect-VIServer -Server $VCenter -Credential $credential

try {
    $dc = Get-Datacenter -Name $Datacenter -Server $viConnection -ErrorAction Stop
    $clusterObject = Get-Cluster -Name $Cluster -Location $dc -Server $viConnection -ErrorAction Stop

    if (-not $Datastore) {
        $availableDatastores = Get-Datastore -RelatedObject $clusterObject | Where-Object { $_.State -eq 'Available' } | Sort-Object FreeSpaceGB -Descending
        if (-not $availableDatastores) { throw "No available datastore was found for cluster '$Cluster'." }
        Write-Host 'Available datastores:'
        $availableDatastores | Format-Table Name,FreeSpaceGB -AutoSize | Out-Host
        $Datastore = Read-Host "Datastore name [default: $($availableDatastores[0].Name)]"
        if (-not $Datastore) { $Datastore = $availableDatastores[0].Name }
    }
    $datastoreObject = Get-Datastore -Name $Datastore -Server $viConnection -ErrorAction Stop
    $targetHost = Get-VMHost -Location $clusterObject -Server $viConnection |
        Where-Object { $_.ConnectionState -eq 'Connected' -and $_.PowerState -eq 'PoweredOn' } |
        Select-Object -First 1
    if (-not $targetHost) { throw "No connected, powered-on ESXi host was found in cluster '$Cluster'." }

    $portGroups = Get-VDPortgroup -Server $viConnection -ErrorAction SilentlyContinue
    if (-not $portGroups) { $portGroups = Get-VirtualPortGroup -Server $viConnection }
    if (-not $portGroups) { throw 'No distributed or standard port groups are visible to this vCenter account.' }
    if (-not $WanPortGroup -or -not $LanPortGroup) {
        Write-Host 'Available port groups:'
        $portGroups | Sort-Object Name | Select-Object Name | Format-Table -AutoSize | Out-Host
        if (-not $WanPortGroup) { $WanPortGroup = Read-Host 'WAN port group name' }
        if (-not $LanPortGroup) { $LanPortGroup = Read-Host 'LAN port group name' }
    }
    $wanNetwork = $portGroups | Where-Object Name -eq $WanPortGroup | Select-Object -First 1
    $lanNetwork = $portGroups | Where-Object Name -eq $LanPortGroup | Select-Object -First 1
    if (-not $wanNetwork) { throw "WAN port group not found: $WanPortGroup" }
    if (-not $lanNetwork) { throw "LAN port group not found: $LanPortGroup" }

    $vmFolder = $dc | Get-Folder -Type VM | Select-Object -First 1
    if ($Folder) { $vmFolder = Get-Folder -Name $Folder -Type VM -Server $viConnection -ErrorAction Stop }
    if (Get-VM -Name $VmName -Server $viConnection -ErrorAction SilentlyContinue) { throw "A VM named '$VmName' already exists." }

    $ovf = Get-OvfConfiguration -Ovf $OvaPath
    $ovf.NetworkMapping.WAN.Value = $wanNetwork
    $ovf.NetworkMapping.LAN.Value = $lanNetwork
    if ($ovf.Common -and $ovf.Common.password) {
        if (-not $VyOSCredential) {
            $VyOSCredential = Get-Credential -UserName vyos -Message 'New VyOS administrator login (password: 12-128 characters)'
        }
        if (-not $VyOSCredential) { throw 'VyOS administrator credentials are required.' }
        $loginName = $VyOSCredential.UserName
        if ($loginName -cnotmatch '^[a-z][a-z0-9_-]{0,31}$' -or $loginName -eq 'root') {
            throw 'Invalid VyOS administrator username.'
        }
        $loginPassword = $VyOSCredential.GetNetworkCredential().Password
        if ($loginPassword.Length -lt 12 -or $loginPassword.Length -gt 128 -or $loginPassword -match '[\x00-\x1f\x7f]') {
            throw 'VyOS password must be 12-128 characters without control characters.'
        }
        if ($ovf.Common.username) { $ovf.Common.username.Value = $loginName }
        $ovf.Common.password.Value = $loginPassword
        $loginPassword = $null
    }

    Write-Host "Deploying $VmName to $VCenter / $Datacenter / $Cluster..."
    $vm = Import-VApp -Source $OvaPath -OvfConfiguration $ovf -Name $VmName -VMHost $targetHost -Location $clusterObject -InventoryLocation $vmFolder -Datastore $datastoreObject -DiskStorageFormat Thin -Force
    if ($ovf.Common -and $ovf.Common.password) { $ovf.Common.password.Value = '' }
    Set-VM -VM $vm -NumCpu $CpuCount -MemoryGB $MemoryGB -Confirm:$false | Out-Null
    if ($VyOSConfigFile) {
        New-AdvancedSetting -Entity $vm -Name 'guestinfo.vyos.config-b64' -Value $vyosConfigPayload -Force -Confirm:$false | Out-Null
        Write-Host "Prepared $VmName to apply VyOS configuration from $(Resolve-Path -LiteralPath $VyOSConfigFile) at first boot."
    }
    if (-not $NoPowerOn) {
        Start-VM -VM $vm -Confirm:$false | Out-Null
        if ($VyOSConfigFile) {
            Write-Host "Deployment complete. $VmName will reboot once after installing the supplied config.boot."
        }
        else {
            Write-Host "Deployment complete. $VmName started; allow first-boot login customization and its reboot to finish."
        }
    }
    else {
        Write-Host "Deployment complete. $VmName was left powered off."
    }

    # Deliberately exclude vCenter credentials and configuration content. Each
    # run reads the configuration file again instead of writing its contents to disk.
    $settingsDirectory = Split-Path -Parent $SettingsPath
    if ($settingsDirectory) { [System.IO.Directory]::CreateDirectory($settingsDirectory) | Out-Null }
    [ordered]@{
        VCenter = $VCenter
        Datacenter = $Datacenter
        Cluster = $Cluster
        VmName = $VmName
        VyOSConfigFile = $VyOSConfigFile
        OvaPath = (Resolve-Path -LiteralPath $OvaPath).Path
        Datastore = $Datastore
        WanPortGroup = $WanPortGroup
        LanPortGroup = $LanPortGroup
        Folder = $Folder
        CpuCount = $CpuCount
        MemoryGB = $MemoryGB
    } | ConvertTo-Json | Set-Content -LiteralPath $SettingsPath -Encoding utf8
    Write-Host "Saved non-secret deployment settings to $SettingsPath"
}
finally {
    $loginPassword = $null
    if ($ovf -and $ovf.Common -and $ovf.Common.password) { $ovf.Common.password.Value = '' }
    Disconnect-VIServer -Server $viConnection -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}

