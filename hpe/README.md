# HPE iLO Redfish

A community Management Pack Builder design for ProLiant inventory, health, fans, temperature, and power monitoring directly through the iLO Redfish API over HTTPS. No bridge appliance is required.

## Downloads

- [Builder design JSON](designs/HPE%20iLO%20Redfish.json)
- No separate HPE release ZIP is published yet.

Exported design version: **1.0.0**. This is a Builder design, not an installable `.pak`. The reviewed export is preserved byte for byte. Import the JSON into Builder; do not rename it to `.pak`.

## Tested environment and status

- ProLiant DL360 Gen9 with iLO 4 Advanced, firmware 2.82.
- VCF Operations **9.1.0.0400.25541561**, recorded in the exported design, with built-in Management Pack Builder.
- Reference server powered off during testing.
- Source connection, full Builder collection, and installation succeeded on August 28, 2026.
- Final verification returned **49 objects, 138 metrics, 244 properties, 48 default relationships, and 0 events**, with no warnings or errors in that collection log. Totals include the adapter instance and Builder collection statistics.
- A runtime account was subsequently added, but its validation and sustained scheduled collection have not been independently verified.

This is a community preview, not an HPE or Broadcom certified management pack. Other ProLiant models, iLO generations, and firmware versions need separate validation.

## Coverage

| Object type | Coverage |
| --- | --- |
| HPE Server | Model, manufacturer, BIOS, serial number, UUID, SKU, power state, health/state, processor model and count, installed memory, power capacity and consumption statistics |
| HPE iLO Controller | Firmware, controller name/type, license edition, state, UUID |
| HPE Fan | Name, location, state, units, speed percent |
| HPE Temperature Sensor | Name, sensor number, physical context, state, units, temperature and critical/fatal thresholds in Celsius |
| HPE Power Supply | Model, firmware, bay, type, serial number, health/state, input voltage, last/average/maximum output watts |

The reference inventory contained one server, one controller, seven fans, 37 temperature sensors, two power supplies, and one adapter instance. Server and controller identities use UUID; fans use name; temperature sensors use sensor number; power supplies use serial number. Builder also includes `adapter_instance_id` to separate configured sources.

Health and state are properties, not custom alert definitions. Powered-off sensors returned zero temperature readings with Offline state. Those values must not be interpreted as actual 0 C measurements. A zero threshold is not automatically a meaningful alert threshold. The two power-supply records reported Absent/Warning in this test; that alone does not establish a hardware failure.

## Before importing

- Use a dedicated iLO account with access to the required Redfish reads. The minimum role was not independently validated.
- Confirm collector DNS resolution and connectivity to iLO HTTPS, normally port 443.
- Use a trusted certificate whose SAN matches the configured hostname or address, with TLS verification enabled.
- Supply ordinary iLO username and password credentials. No password encoding procedure is required.
- The exported hostname default is blank and TLS defaults to Verify. Credentials are references, not stored values.

## Connection and requests

Use HTTPS, Basic authentication, and base path `redfish/v1` without a leading slash. Builder adds the separator. Session authentication is disabled. The source uses the generated Basic authentication header, `Content-Type: application/json`, and `Connection: close`.

| Purpose | Method and full path |
| --- | --- |
| Source connection test and Server | GET `/redfish/v1/Systems/1/` |
| Thermal | GET `/redfish/v1/Chassis/1/Thermal/` |
| Power | GET `/redfish/v1/Chassis/1/Power/` |
| iLO Controller | GET `/redfish/v1/Managers/1/` |

All requests are read-only GET requests; pagination is disabled. The fixed resource ID `1` and mapped fields were validated against the reference iLO 4 only. No power-control, firmware-update, or configuration actions are included.

## Import and configure

1. Download the design JSON. Preserve existing designs and use a separate test copy when needed.
2. Open **Build > Developer Center > Management Pack Builder > Import** and select the JSON.
3. Configure the source collector, iLO hostname, HTTPS port, and dedicated credentials.
4. Keep TLS verification enabled and resolve certificate trust, name matching, and collector DNS/connectivity issues.
5. Test the source and each request. Check actual returned fields against the mappings, especially on other firmware.
6. Run **Verify > Perform Collection**. Inspect the log, object inventory, identities, metric values, and states. Counts may differ on other hardware.
7. Install the validated pack through Builder.
8. In **Integrations**, locate **HPE iLO Redfish** and add an account with its own host, collector, TLS configuration, and credentials. Builder test credentials are separate from runtime credentials.
9. Validate the account and check at least two scheduled cycles, fresh timestamps, and values against iLO before relying on monitoring.

## Troubleshooting

- HTTP failed-to-respond errors: the reference iLO intermittently failed when connections were reused. Adding `Connection: close` resolved the observed request failures. Retest the complete collection after changing headers.
- A successful preview badge is not sufficient: earlier previews skipped the server despite reporting success. Inspect logs and actual inventory. The final clean test included all five hardware object types.
- 401/403: check credentials and access to the required resources.
- TLS errors: fix trust and certificate naming from the collector's network perspective. The lab source used No Verify; this disables certificate identity verification and is not the recommended deployment setting. Do not switch to HTTP.
- Zero or unexpected sensor values: check the device power state and the API's sensor state before interpreting the numeric reading.
- Builder succeeds but runtime fails: verify the runtime account separately, including its credentials and collector network path.

## Limitations

- No individual disk, RAID, storage-controller, DIMM, or CPU objects.
- No custom dashboards, alert definitions, event mappings, or server-to-component topology. The 48 relationships in verification were Builder defaults.
- iLO 5, iLO 6, other resource IDs, and other firmware are untested. This design uses fields observed on iLO 4, including fan `CurrentReading`.
- Powered-on fan, temperature, and power behavior still needs validation.
- Installation and a clean Builder test do not prove sustained runtime collection.

## Security

Do not publish credentials, raw responses, private addresses, hostnames, or device identifiers in issues or screenshots. Use HTTPS with certificate verification and dedicated credentials. See the repository [security guidance](../SECURITY.md).
