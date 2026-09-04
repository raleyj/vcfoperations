# HPE iLO Redfish

A community VCF Operations Management Pack Builder design for read-only HPE ProLiant monitoring through the iLO Redfish API.

**Status as of September 4, 2026:** the existing lab pack was upgraded in place to generated package **1.0.0.7**. Development and further testing are paused. The download contains the latest installed Builder design; the limitations below remain unresolved and are not completion claims.

## Downloads

- [HPE iLO Redfish design JSON](designs/HPE%20iLO%20Redfish.json)
- [Validation results and known limitations](VALIDATION.md)

This is a Builder design JSON, not an installable `.pak`. The exported design version remains **1.0.0**; **1.0.0.7** is the generated package version observed in the existing lab installation. Package numbering in another environment can differ. The JSON was exported September 3 and used for the verified September 4 upgrade. It contains 11 object types, 18 requests and two event mappings. No SDK replacement or standalone content bundle is released.

SHA-256 of the exact published JSON:

```text
f02e2e1370a63b5c8ad9a31f6c46f6373686b5a6217367947e7a35a8108d7d21
```

## Tested environment and status

Built for best-effort **iLO 4 through iLO 7** Redfish compatibility, but tested only on an **HPE ProLiant DL360 Gen9 with iLO 4 firmware 2.82**, using VCF Operations **9.1.0.0400.25541561**. Other generations were reviewed against HPE emulator data, not validated on hardware. This is not support for every firmware or server model. iLO 1 through 3 and non-Redfish firmware are outside scope; no vendor certification is claimed.

The latest native scheduled baseline contained **92 hardware objects** and **216 metrics**. Operations reported **93 collected objects**, including the adapter account. Four consecutive direct collections after test cleanup retained these counts and fresh fan readings. The server had **91 component children**, covering all other hardware objects in this lab inventory. These supersede the earlier 54-child topology result.

Builder preview totals and native scheduled totals count different content. The earlier 227-metric preview must not be presented as the current native 216-metric result. An installed status or Data receiving label alone does not establish complete or fresh collection.

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
| HPE Fan (iLO 4) | Name, location, state, speed percentage and explicit Fan Health property |
| HPE Temperature Sensor | Name, context, state, temperature, thresholds and explicit Sensor Health property |
| HPE Power Supply | Bay, model, serial, firmware, health, voltage and output readings |
| HPE Firmware Component | Component name, location and installed version |

The live inventory comprised one server, one iLO controller, two processors, 16 DIMMs, one storage controller, three logical drives, seven physical drives, seven fans, 37 temperature sensors, two power supplies and 15 firmware components. The current download has these eleven object definitions; older descriptions of separate modern-only fan and system-power object types do not describe this export. Cross-generation compatibility remains a design target, not a verified result.

### Server topology

The revised relationships linked all 91 components to the server while preserving existing object identities. The design uses a constant match within its single-server collection model because many component responses do not repeat the ComputerSystem UUID. Configure **one iLO endpoint per adapter account**. Do not assume multi-server aggregation or cross-account isolation has been established by this single-account test.

### Operational content

Nine hardware-health alert definitions and an HPE dashboard with six collection diagnostic charts were configured separately in the lab. Fan and temperature alerts require explicit Warning/Critical health plus Enabled state; the power-supply guard also requires Enabled state. These definitions and the dashboard are **not bundled in the JSON**. Native content export was blocked by the browser, and separate import/rollback was not verified.

## Before importing

Use dedicated credentials with the minimum required Redfish read permissions. Confirm HTTPS reachability from the collector and use a trusted certificate whose SAN matches the configured hostname or address. The public export has a blank hostname, credential references rather than credential values, and TLS default **Verify**. Back up the existing design and Operations configuration; a JSON backup does not preserve collected history or separate content.

## Connection and requests

The design uses HTTPS Basic authentication and read-only GET requests under `redfish/v1`, including system, manager, thermal, power, processor, memory, Smart Storage, firmware inventory, Integrated Management Log (IML) and iLO Event Log resources. `Connection: close` is retained for the tested iLO 4. Defaults are port 443, a 30-second timeout, two concurrent requests, two retries and minimum event severity Warning. Endpoint IDs and OEM fields vary by platform; inspect actual responses before deployment.

No firmware update, power-control, log-clearing or configuration-changing hardware action is included. The temporary response relay used for controlled tests was removed from the collection path and stopped; it is not a deployment dependency.

## Import and configure

1. Download the JSON and verify its SHA-256. Do not rename it to `.pak` or upload a design ZIP to a package installer.
2. Open **Build > Developer Center > Management Pack Builder**. For a new installation, import the JSON.
3. For an existing installation, back up and update the existing design in place. Duplicate-name import is not a verified upgrade workflow. Do not uninstall to resolve a name conflict: uninstall can delete associated data, metadata and content. Retain the existing account and object identifiers.
4. Configure the source collector, hostname, HTTPS port and dedicated credentials. Keep TLS verification enabled and correct certificate trust, SAN matching and DNS.
5. Test every request, then run **Verify > Perform Collection**. Inspect logs, expected inventory, sensor states and server relationships.
6. Install or upgrade through Builder. Retain one runtime account per iLO endpoint; Builder source credentials and runtime credentials are separate.
7. Verify advancing timestamps and expected counts over scheduled collections. For an upgrade, compare object identities, relationships and existing history before and after.
8. Configure any desired dashboard and alerts separately. The tested lab definitions are not delivered as an importable content bundle.

The lab Builder upgrade preserved its existing account and resource identities. This does not establish a general migration guarantee or an SDK upgrade path.

## Troubleshooting

- **Missing or stale data:** the current pack can retain a previous health value after its field disappears. Data receiving and zero no-data counts did not reliably expose partial failures. Inspect current metric counts, timestamps and endpoint errors; do not rely on retained health as current.
- **Sensor interpretation:** require state and health context. Offline temperature zero is not a real zero-degree reading. A physical-drive reading of 255 C with a maximum of 0 C was observed as an apparent unavailable-value sentinel, not confirmed overheating.
- **Power supplies and fans:** an absent bay or zero fan speed is not automatically a hardware fault. Use Enabled-state guards and power context.
- **401/403:** verify source/runtime credentials and permission for each Redfish resource separately.
- **TLS:** fix trust and hostname matching, not by switching to HTTP or disabling verification. Rejection of a changed untrusted certificate was tested; hostname-mismatch rejection remains unverified.
- **Inventory or topology gaps:** inspect request logs and identifiers even if collection reports success. Compare against expected inventory for the device, not this lab's totals.

### Events

The IML mapping combines source severity with the legacy `Oem.Hp.Repaired` value; Warning/Critical unrepaired entries are eligible for collection. The separate iLO Event Log mapping also remains in the design. Controlled response-copy tests verified IML event creation, no duplicates for unchanged delivery, and basic repair clearing after three cycles. They did not modify the hardware log or generate a physical fault.

Missing Repaired metadata caused a test event to be omitted. Changing only Created while retaining RecordId and message did not distinguish a new generation. One later synthetic event remained uncanceled after four direct recovery cycles. Event behavior across missing data, restarts, log resets and account changes is therefore not fully reliable. See [validation details](VALIDATION.md).

## Limitations

- Physical testing is limited to iLO 4 firmware 2.82 on the DL360 Gen9. Fixed IDs, legacy OEM fields and optional endpoint differences may require adaptation elsewhere.
- Explicit unknown/stale health and corresponding alert behavior remain incomplete. A retained Critical value persisted when Fan Health was omitted.
- Scheduled server power-off/transition testing and certificate hostname rejection remain unverified.
- Separate native dashboard/alert export, import and rollback remain unverified; no content bundle or standalone `.pak` is published.
- Missing repair metadata and durable event generation/clearing have known gaps. One labeled synthetic test event remains uncanceled in the lab; no test entry was written to the hardware IML.
- An SDK feasibility prototype passed seven offline tests only. No SDK pack or cloud proxy was deployed, and identity/history preservation, durable storage and native SDK behavior remain unverified. SDK work was restricted to investigation and is not part of this download.

The three remaining roadmap areas are recorded as **known limitations with further work paused**, not completed features or a commitment to further development. See [the validation summary](VALIDATION.md) for the distinction between completed checks and unresolved behavior.

## Security

Use HTTPS with verification and least-privilege credentials. Do not publish credentials, private hostnames or addresses, raw responses, logs, device UUIDs or serial numbers. Published files contain the design and a sanitized test summary, not lab credentials, relay keys or private inventory. See [SECURITY.md](../SECURITY.md).
