# Dell iDRAC compatibility

The project uses Redfish and supports two endpoint families. This distinction is
required because a single Builder response mapping cannot safely interpret both
the legacy aggregate documents and the newer subsystem resources.

| Profile | Intended targets | Resource family | Status |
| --- | --- | --- | --- |
| Legacy | iDRAC7/8 and iDRAC9 where aggregate resources remain available | `Systems/{id}`, `Chassis/{id}/Power`, `Chassis/{id}/Thermal` | Builder-tested on iDRAC9 7.20.30.00 |
| Modern | Newer iDRAC9 and iDRAC10 | `Systems/{id}`, `PowerSubsystem`, `ThermalSubsystem`, and `Sensors` | Schema-reviewed; hardware validation required |

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
- Use the legacy design only when both aggregate endpoints return HTTP 200.
- Treat missing or null sensor values as unavailable, never as zero.
- Validate a full Builder collection and two scheduled runtime cycles before
  treating a firmware or hardware model as supported.

The current importable design remains the legacy profile. A modern Builder
design must be generated and tested against an iDRAC that exposes the modern
documents before it can be published as supported; schema review alone is not a
substitute for that test.

