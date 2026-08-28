# VyOS Router OVA for VMware

This folder contains deployment guidance and rebuild files for a lab VyOS router
appliance with open-vm-tools and deployment-time administrator credentials.

> This is a community lab build, not an official VyOS image or a production-hardened
> router. Review the security notes and validate traffic in your own environment.

## Download

Download **VyOS-Router.ova** from the
[VyOS Router OVA 2026.03 release](https://github.com/raleyj/vcfoperations/releases/tag/vyos-2026.03-1).

- Size: 993,266,176 bytes
- SHA-256: `6a3a233fb60236a7e66ab18b2a45f182a578495cc70fc563db82a482c609899d`
- Base: VyOS 2026.03 (circinus)
- VMware Tools: open-vm-tools 12.2.0.41219 (build 21223074)

Verify after download:

```powershell
Get-FileHash .\VyOS-Router.ova -Algorithm SHA256
```

## Appliance profile

| Resource | Default |
| --- | --- |
| CPU | 2 vCPU |
| Memory | 4 GiB |
| Disk | 10 GiB, thin-capable PVSCSI |
| NIC 1 | VMXNET3, WAN / eth0 |
| NIC 2 | VMXNET3, LAN / eth1 |

Without an injected configuration, eth0 uses DHCP and SSH is enabled. No
production firewall policy is included.

## Deploy in vCenter

1. Select **Deploy OVF Template** and choose the downloaded OVA.
2. Select the VM location, compute resource and datastore.
3. Map WAN and LAN to isolated test port groups.
4. Under **Customize template**, set the administrator username and password.
   The password must be 12–128 characters without control characters.
5. Complete deployment, inspect the VM and power it on.
6. Wait for first-boot customization and its reboot before logging in.
7. Review interfaces, firewall policy and routing before connecting live networks.

The bootstrap login is `vyos/vyos` until successful customization completes. A
manual import that supplies no login properties or configuration retains that
login. Deploy on an isolated or trusted network.

The masked property is not encrypted metadata. Privileged platform administrators
may retrieve it. Do not redistribute a configured VM with deployment credentials.

## Automated deployment and configuration

`deploy-vyos-vcenter.ps1` imports the OVA through PowerCLI. Set your actual vCenter,
datacenter, cluster, datastore and port-group names. Pass a complete config.boot
with `-VyOSConfigFile`; use `-NoPowerOn` to inspect the imported VM first.

```powershell
$routerCredential = Get-Credential -UserName vyos
.\deploy-vyos-vcenter.ps1 `
  -OvaPath .\VyOS-Router.ova `
  -VCenter vcenter.example.com `
  -Datacenter Datacenter `
  -Cluster Cluster `
  -Datastore datastore1 `
  -WanPortGroup VyOS-WAN `
  -LanPortGroup VyOS-LAN `
  -VyOSCredential $routerCredential `
  -NoPowerOn
```

The script can inject a configuration through `guestinfo.vyos.config-b64` before
first boot. Base64 is not encryption. Remove the setting after confirming success.
Never commit credentials or private configuration files.

## Validation status

Two isolated vCenter imports of this exact OVA passed:

- New `routeradmin` username and password; default account removed.
- Existing `vyos` username with a new password plus injected VLAN/DHCP/NAT/BGP config.
- Old `vyos/vyos` login rejected in both cases.
- VMware Tools and VyOS router services active; no failed systemd units.
- Credentials and configuration persisted across an additional reboot.
- OVA TAR structure, manifest references, hashes and OVF properties verified.

NICs remained disconnected. Live DHCP exchanges, routing/NAT traffic, VLAN
connectivity and BGP peering were not tested. See [VALIDATION.md](VALIDATION.md).

## Rebuild

`VyOS-Router-Rebuild-Kit.zip` contains the PowerShell, Ansible and first-boot source
used for the reconstruction. Supply the matching VyOS ISO separately; the ISO and
OVA are deliberately excluded from the kit. Docker Desktop with Linux containers,
PowerShell 7 and VMware OVF Tool are required.

The recorded input ISO SHA-256 is
`56151a536e4a70c1a3f9202d8e6e59e7dd308cc84e2c50b633884a1376a39010`.
This records the local input; it is not independent publisher authentication.

Product names and trademarks belong to their respective owners. Review the
licenses of VyOS and all included software before redistribution or production use.
