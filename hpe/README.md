# HPE iLO Redfish

A community VCF Operations Management Pack Builder design for read-only HPE ProLiant monitoring through the iLO Redfish API.

## Downloads

- [HPE iLO Redfish design JSON](designs/HPE%20iLO%20Redfish.json)

This is a Builder design JSON, not an installable `.pak`. Import it through Management Pack Builder and install it from there. The exported design version remains **1.0.0** because Builder preserves that internal value when upgrading the existing design.

SHA-256 of the September 3, 2026 reviewed export:

```text
0e213c06eeedf9100e60220ed3d7eac4016fd2f958f091c4bca24607002e18e3
```

## Tested environment and status

The design was built for best-effort iLO 4 through iLO 7 Redfish compatibility. It has only been tested on:

- HPE ProLiant DL360 Gen9
- iLO 4 firmware 2.82
- VCF Operations 9.1.0.0400.25541561

iLO 5, 6, and 7 mappings were reviewed against HPE emulator data but could not be verified on physical hardware. iLO 1 through 3 and non-Redfish firmware are outside scope. This is a community design, not an HPE or Broadcom certified management pack.

The September 3 powered-on Builder collection completed successfully in 51 seconds with:

- **93 objects**
- **227 metrics**
- **529 properties**
- **146 relationships**
- **0 events**

The server object showed **54 collected component relationships**. The existing management pack was then upgraded in place and retained its design identity and configured account.

## Coverage

| Object type | Main data collected |
| --- | --- |
| HPE Server | Model, serial, UUID, BIOS, health, power state, processor and memory summaries, power readings |
| HPE iLO Controller | Firmware, controller identity, license, health and state |
| HPE Processor | Socket identity, model, cores, threads, speed and health |
| HPE DIMM | Location, capacity, type, speed, rank and health |
| HPE Storage Controller | Model, firmware, location, status and cache data |
| HPE Logical Drive | Redfish identity, capacity, RAID and status |
| HPE Physical Drive | Location, model, firmware, media/interface details, capacity, speed, temperature and status |
| HPE Fan (iLO 4) | Name, location, state and speed percentage |
| HPE Temperature Sensor | Name, context, state, current temperature and thresholds |
| HPE Power Supply | Bay, model, serial, firmware, health, voltage and output readings |
| HPE Firmware Component | Component name, location and installed version |

The design also contains modern HPE fan and power mappings for best-effort iLO 5 through iLO 7 compatibility. Unsupported mappings can be skipped when the corresponding API shape is absent.

### Server topology

Component objects are related to the single HPE Server collected by each adapter account. The validated iLO 4 account returned 54 server children across firmware, memory, processors, storage, fans, power supplies and temperature sensors.

The relationship expressions intentionally use an account-scoped constant match because many iLO component responses do not repeat the ComputerSystem UUID. Configure one iLO endpoint per adapter account. Do not combine multiple servers behind one account.

## Before importing

Use a dedicated read-only iLO account, confirm HTTPS reachability from the collector, and use a trusted certificate whose SAN matches the configured hostname. Back up an existing Builder design before editing it. The exported hostname is blank and no credential value is included.

## Connection and requests

The design uses HTTPS Basic authentication and read-only Redfish GET requests under `redfish/v1`. It covers the system, manager, thermal, power, processor, memory, Smart Storage, firmware inventory and iLO event log resources available on the tested server. `Connection: close` is retained because it resolved intermittent response failures observed with iLO 4. Resource identifiers and endpoint availability can differ on later platforms.

## Import and configure

1. Download `HPE iLO Redfish.json` without renaming it.
2. In VCF Operations, open **Build > Developer Center > Management Pack Builder**.
3. Import the JSON. If an HPE iLO Redfish design already exists, update that design in place; Builder rejects another design with the same name.
4. Configure the source collector, iLO hostname, HTTPS port and dedicated read-only iLO credentials.
5. Keep TLS certificate verification enabled. The certificate SAN must match the configured hostname and the collector must trust the issuing CA.
6. Test the source and every request. API availability and field names vary by iLO generation.
7. Run **Verify > Perform Collection**. Inspect the log, object inventory, values and the HPE Server relationship list.
8. Install or upgrade through Builder.
9. In **Operations > Integrations**, configure or retain one runtime account per iLO endpoint.
10. Confirm that the account is collecting and that timestamps advance across scheduled cycles before relying on alerts.

Builder test credentials and runtime integration credentials are separate.

## Troubleshooting

- Treat absent data as unknown, not healthy or zero.
- Gate temperature interpretation on sensor state and validity. A physical-drive value of `255 C` with a maximum of `0 C` was observed as a sentinel and must not be treated as a real overheating condition.
- Do not alert on zero fan speed without also evaluating power state, fan state and health.
- An absent redundant power-supply bay is inventory state, not automatically a failure.
- Keep collection-health and data-age alerts separate from hardware-health alerts.
- Suppress or maintain alerts during planned iLO and server maintenance.

### Events

The design maps iLO Event Log entries at Warning and Critical severity. The tested iLO 4 log contained only OK entries, so the September 3 verification returned zero events. Event creation, deduplication and recovery could not be proven without generating a real warning or failure and should be validated safely in each environment.

### Common issues

- **401/403:** verify the account and permissions for every requested Redfish resource.
- **TLS validation fails:** fix certificate trust, SAN matching and collector DNS. Do not switch to HTTP.
- **Successful collection but missing objects:** inspect the full log and identifiers; the success badge alone does not prove complete inventory.
- **Server has no component relationships:** verify that the current design is installed and inspect the server relationship list after a new collection.
- **Unexpected temperature values:** check health/state and device-specific sentinel values before alerting.
- **Builder succeeds but runtime fails:** verify the runtime account, collector path and scheduled timestamps separately.

## Limitations

- Physical validation is limited to iLO 4 firmware 2.82 on a DL360 Gen9.
- Fixed Redfish resource IDs and optional OEM fields may require adjustment on another platform.
- The topology model assumes one iLO server per adapter account.
- No firmware update, power-control or configuration-changing action is included.
- No destructive hardware fault was generated during validation.
- Event deduplication and recovery remain unverified because the available event log contained no Warning or Critical record.
- Custom dashboards and alert definitions are documented operational recommendations, not bundled content in this Builder JSON.

## Security

Use HTTPS with verification and a dedicated least-privilege iLO account. Do not publish credentials, private hostnames or addresses, raw API responses, logs, device UUIDs or serial numbers. See the repository [security guidance](../SECURITY.md).
