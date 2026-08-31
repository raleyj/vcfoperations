# Dell iDRAC compatibility

The project distinguishes two Redfish endpoint families; this is not a claim of
validated support for both. This distinction is
required because a single Builder response mapping cannot safely interpret both
the legacy aggregate documents and the newer subsystem resources.

| Profile | Intended targets | Resource family | Status |
| --- | --- | --- | --- |
| Legacy | iDRAC7/8 and iDRAC9 where aggregate resources remain available | `Systems/{id}`, `Chassis/{id}/Power`, `Chassis/{id}/Thermal` | Builder-tested on iDRAC9 7.20.30.00 |
| Modern | Newer iDRAC9 and iDRAC10 | `Systems/{id}`, `PowerSubsystem`, `ThermalSubsystem`, and `Sensors` | Experimental candidate; synthetic tests pass; hardware validation required |

## Probe a controller

The probe performs GET requests only, discovers the actual system and chassis
resource IDs, checks both resource families, and does not print credentials.

```powershell
$env:IDRAC_USERNAME = 'monitoring-user'
$env:IDRAC_PASSWORD = Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText
python .\tools\probe_idrac_redfish.py idrac.example.com
Remove-Item Env:IDRAC_USERNAME, Env:IDRAC_PASSWORD
```

Use `--no-verify` only for an isolated lab. A trusted certificate whose SAN
matches the configured hostname is the recommended configuration.

## Compatibility rules

- Do not assume `System.Embedded.1`; discover IDs from `/redfish/v1/Systems` and
  `/redfish/v1/Chassis`.
- Prefer modern subsystem links advertised by the Chassis resource.
- HTTP 200 alone is insufficient: compare legacy response shapes, properties and
  actual paths with the design before testing collection.
- Treat missing or null sensor values as unavailable, never as zero.
- Validate a full Builder collection and two scheduled runtime cycles before
  treating a firmware or hardware model as supported.

The legacy design remains the only hardware-tested profile. A separate
[Modern Redfish Candidate](experimental/modern/README.md) is available with
synthetic fixtures and nine local tests. Imported into VCF Operations 9.1 on
August 31, 2026 as a separate Invalid / Draft design; source configuration and
Builder verification remain incomplete. It has not been installed and does not
replace the legacy pack. No real iDRAC10 or modern iDRAC9 collection was tested.

The probe currently examines the first system/chassis and does not traverse
pagination. Multi-chassis targets need manual review. Resource detection does not
validate metric mappings. iDRAC6 and firmware without Redfish are outside scope;
iDRAC7/8 require Redfish-capable firmware and independent validation.
