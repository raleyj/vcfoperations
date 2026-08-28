# Deployment-login OVA validation — 2026-08-28

## Delivered OVA

- File: `dist/VyOS-Router.ova`
- Size: 993,266,176 bytes.
- SHA-256: `6a3a233fb60236a7e66ab18b2a45f182a578495cc70fc563db82a482c609899d`
- Base: VyOS 2026.03 (circinus), from the locally retained ISO.
- ISO SHA-256: `56151a536e4a70c1a3f9202d8e6e59e7dd308cc84e2c50b633884a1376a39010`

The prior config-only OVA is preserved locally under `dist/previous-config-only`.
This new OVA supersedes it with deployment-time administrator login properties.

## Verified properties

VMware OVF Tool reports both properties under **VyOS administrator login**:

| Property | Label | Type | Default |
| --- | --- | --- | --- |
| `username` | Administrator username | string, 1-32 characters | `vyos` |
| `password` | Administrator password | masked password, 12-128 characters | none |

The guest additionally validates the username, rejects reserved system accounts,
and rejects passwords containing control characters. Credentials are applied
once after persistent configuration initialization, followed by one reboot.

## Validation completed

- Ansible build: zero failed or rescued tasks.
- OVF Tool export and `--verifyOnly`: passed.
- Independent TAR/OVF reference-size and manifest-hash checks: passed.
- Verified both user-configurable properties and the password masking attribute;
  the OVA contains no deployment password value.
- Eight tests passed using the real VyOS ConfigTree library: account creation,
  rename, password replacement, supplied-config precedence, no-customization
  behavior, XML namespaces, invalid credentials, and malformed input handling.
- Password hashing was tested with XML/shell special characters.
- PowerShell syntax checks and existing configuration-generator tests passed.

Two fresh imports of the **exact delivered OVA** were booted in VMware Workstation
with both network adapters disconnected:

1. **OVF login only:** `routeradmin` with a generated test password. Login and sudo
   succeeded; `vyos` was absent from both the active config and OS account database.
   The former `vyos/vyos` login was explicitly rejected.
2. **OVF login plus config.boot:** kept username `vyos`, supplied a new password,
   and injected the VLAN/DHCP/NAT/BGP test configuration. The new password worked,
   the old `vyos` password was rejected, the hostname and VLAN/BGP config persisted,
   and Kea DHCP and FRR were active.

Both tests reported active VMware Tools and VyOS router services, zero failed
systemd units, a persistent first-boot completion marker, and SHA-512 password
hashes without a plaintext-password node for the configured administrator.
VMware Tools version: **12.2.0.41219 (build-21223074)**.

The delivered first-boot Python source matches the file read inside both guests:
`665e7fc8595ad8749d5196c8417a75d10e128e730145247a513916ff35ff6c41` (SHA-256).

## Live vCenter deployment retest

The exact OVA above was imported twice through PowerCLI into vCenter on
2026-08-28, in the lab vCenter environment. Both NICs were disconnected
before first power-on and remained disconnected. No existing router was changed.

- Login-only deployment: `routeradmin` login and sudo passed; default `vyos`
  account removed and `vyos/vyos` explicitly rejected.
- Login plus injected configuration: new `vyos` password passed; old password
  rejected; expected hostname, VLAN/BGP configuration and active Kea/FRR confirmed.
- Both guests had active Tools/router services, no failed units, persistent
  completion markers and hashed passwords without plaintext-password nodes.
- Both guests were explicitly rebooted again. Distinct guest boot IDs confirmed
  the reboots; all acceptance checks and old-password rejection passed again.
- vCenter imported username and password as user-configurable properties, with
  password type `password(12..128)`. The native OVF environment reached the guest;
  no manually fabricated guestinfo.ovfEnv was used for these tests.
- Early probes during startup were not ready; checks passed after initialization.
  VMware Tools availability alone does not mean VyOS initialization is complete.
- The deployment script now imports the installed VimAutomation.Core module
  instead of requiring the PowerCLI umbrella, and its public defaults use generic example targets. Set the actual
  inventory names for your environment. OVA contents and SHA-256 are unchanged.
- Both temporary vCenter VMs and their disks were removed after verification.

Evidence: private validation reports retained outside this public package.
The source ZIP was refreshed with the corrected deployment script and report.

## Test scope and security notes

The browser-based vCenter deployment wizard was not clicked through; live import
and property delivery were tested through vCenter's PowerCLI API. Earlier local
Workstation tests supplied standard `guestinfo.ovfEnv` XML explicitly because
OVF Tool's VMX-target import does not deliver an OVF environment.

Live DHCP exchanges, routing/NAT traffic and BGP peering were not tested because
all test NICs remained disconnected. The input ISO hash was measured locally;
independent publisher signature verification was not performed.

All local test VMs are shut down. The temporary build container was removed;
the builder image remains. Temporary OVF login metadata was removed from the
stopped test VMX files. Test credentials are not in the source ZIP or OVA.

The bootstrap login remains `vyos/vyos` until successful first-boot customization.
Deploy on a trusted network and wait for the reboot before using the new login.
Masked properties are not encrypted guest metadata: privileged platform/VM
administrators may retrieve them. Do not distribute configured VM files with
deployment credentials still present. Only the password hash is stored in the
guest's active config.boot.

Evidence: `deployment-login-build.log`, `tests/login-unit-results.txt`,
`tests/vm-login-ovf/validation.json`, `tests/vm-login-config/validation.json`, and
`dist/checksums.json`.

