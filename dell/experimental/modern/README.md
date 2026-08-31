# Dell iDRAC Modern Redfish Candidate 0.1.0

**Experimental development artifact, not confirmed iDRAC9/iDRAC10 support.**
The installed legacy Dell pack is unchanged. This folder is deliberately outside
`dell/designs` and excluded from stable design archives.

## Contents and scope

- `Dell iDRAC Modern Redfish Candidate.json`: separate Builder design, 15 requests,
  seven object types. No credentials, blank host, TLS verification default.
- `build_candidate.py`: deterministic generator using the legacy export's source
  envelope. Run from a repository checkout; it reads `dell/designs`.
- `mock_redfish.py`: GET-only loopback HTTP service with synthetic fixtures for
  two servers/chassis. These are NOT captured Dell firmware responses or a
  complete Redfish emulator. No authentication or TLS simulation.
- `test_candidate.py`: independent fixture evaluator and nine regression tests.
  It does not execute the VCF Builder collector.

The design follows service-root Systems/Chassis links and collection members,
then EnvironmentMetrics, PowerSubsystem/PowerSupplies/Metrics,
ThermalSubsystem/Fans, and Sensors. It does not hard-code System.Embedded.1.
Objects use resource URI identity. PSU inventory and metrics are separate objects;
there are no custom topology relationships, alerts, dashboards, or events.

## Reading semantics

| Resource field | Meaning |
| --- | --- |
| EnvironmentMetrics.PowerWatts.Reading | Watts |
| EnvironmentMetrics.TemperatureCelsius.Reading | Celsius |
| PowerSupplyMetrics.InputPowerWatts.Reading / OutputPowerWatts.Reading | Watts |
| PowerSupplyMetrics.InputVoltage.Reading | Volts |
| Fan.SpeedPercent.Reading | Percent, not RPM |
| Sensor.Reading | Interpret with ReadingUnits and ReadingType properties |

Builder unit metadata is left blank; explicit field labels retain the unit where
the schema defines one. Generic sensor readings must not all be graphed as Celsius.
Missing/null readings remain unavailable in the fixture evaluator; zero remains zero.

## Reproduce local checks

From the repository root with Python 3 (standard library only):

```text
python dell/experimental/modern/build_candidate.py
python -m unittest discover -s dell/experimental/modern -p test_candidate.py -v
python dell/experimental/modern/mock_redfish.py --port 8088
```

The final command serves `http://127.0.0.1:8088/redfish/v1/` until Ctrl+C.
It does not expose a LAN listener. A remote VCF collector cannot use this
workstation's localhost address. Arrange a separately approved, isolated test
endpoint reachable by the collector before attempting Builder mock collection.
Never send actual iDRAC credentials to this unauthenticated HTTP fixture service.

## Validation and known gaps

Nine local tests pass: reproducible export, multi-chassis identities and sensor
units, missing optional branch, empty collection, rejected pagination, rejected
external URI, missing endpoint, invalid numeric value, and an HTTP GET smoke test.
The fixture graph emits 18 custom objects. This is NOT a VCF collection count.
Static export checks pass for references, blank hostname, TLS default and absence
of credential values.

The evaluator skips missing optional links and rejects foreign URLs, malformed
readings and pagination. These are evaluator behaviors, not implemented Builder
fallbacks or proven runtime security controls. Builder's null handling, request
chaining, root-relative URI joining, redirects, cross-origin links, optional 404s,
403/401 responses and pagination still need testing. The design has no automatic
legacy fallback and no nextLink traversal. Do not use it against paginated
collections until that is implemented and validated. No timeout, authentication,
TLS, firmware, license or sustained-collection compatibility is claimed.

Import as a NEW design under Build > Developer Center > Management Pack Builder.
Do not replace or install over the working legacy pack. Configure a test source,
inspect every request, compare values with real iDRAC data, and run full Builder
verification. Only after those pass should an isolated installation and at least
two scheduled collection cycles be attempted. Real modern iDRAC validation remains
required before declaring hardware support. Pre-Redfish controllers are outside scope.

## Schema references

Mappings are based on DMTF standard properties, not a claim that every Dell
firmware exposes them:

- [EnvironmentMetrics 1.3.0](https://redfish.dmtf.org/schemas/v1/EnvironmentMetrics.v1_3_0.json)
- [PowerSupplyMetrics 1.1.0](https://redfish.dmtf.org/schemas/v1/PowerSupplyMetrics.v1_1_0.json)
- [Fan 1.5.2](https://redfish.dmtf.org/schemas/v1/Fan.v1_5_2.json)
- [Sensor 1.9.0](https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_0.json)

### VCF import result — August 31, 2026

VCF Operations 9.1 accepted this JSON as a separate design. It shows
**Invalid / Draft**, with source configuration required and Verify not started.
Requests and Objects are marked completed in the import UI, but their screens
remain disabled until source setup. No Builder collection or installation was
performed. The existing Dell iDRAC Redfish pack remains Verified / Installed.
