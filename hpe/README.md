# HPE iLO Redfish

A community Management Pack Builder design for ProLiant inventory, health, fans, temperature, and power monitoring directly through the iLO Redfish API over HTTPS. No bridge appliance is required.

## Downloads

- [Current Builder design JSON](designs/HPE%20iLO%20Redfish.json) — August 31, 2026 replacement with legacy and modern Redfish mappings.
- No separate HPE release ZIP or installable `.pak` is published. Import the JSON into Builder and install through Builder; do not rename it to `.pak`.
- The previous five-object-type design remains available in this file's Git history.

**Version note:** the development candidate was called Universal 1.1.0. After import, renaming, verification, and installation, Builder exported the installed design as **HPE iLO Redfish, version 1.0.0**; Operations displayed generated package version **1.0.0.1**. This download preserves the actual exported values. Identify this update by its August 31 date, seven object types, and SHA-256 below, not by a higher version number.

SHA-256: `8b2e7bf1d479a76a09412c905b1f69a1d5923fdcffbd71268d28f3044582fd49`

## Tested environment and status

- ProLiant DL360 Gen9 with iLO 4 Advanced firmware 2.82; server powered off.
- VCF Operations **9.1.0.0400.25541561** with built-in Management Pack Builder.
- On August 31, 2026, source connectivity, full Builder collection, and replacement installation succeeded.
- Final collection: **49 objects, 140 metrics, 244 properties, 48 default relationships, and 0 events** in six seconds. Totals include the adapter instance and Builder collection statistics.
- The collection was successful but **not warning-free**: eight missing-identifier warnings skipped seven modern fan records and one modern system-power record on iLO 4. The expected legacy hardware inventory was present.
- The earlier August 28 design collected 49 objects and 138 metrics without warnings. Those results describe the previous design, not this replacement.
- Runtime integration-account validation and sustained scheduled collection have not been independently verified for the replacement.

**Compatibility disclaimer:** best-effort mappings target Redfish-capable iLO 4 through iLO 7. Only the reference iLO 4 system was tested live. iLO 5, 6, and 7 were audited offline against seven [official HPE emulator mockups](https://github.com/HewlettPackard/ilo-redfish-emulator), not physical hardware or an executing Builder collector. This is not a claim of support for every firmware release or server model. iLO 1–3 and non-Redfish firmware are outside scope. No HPE or Broadcom certification or support commitment is claimed.

## Coverage

| Object type | Coverage |
| --- | --- |
| HPE Server | Inventory, UUID, serial, BIOS, CPU/memory summary, health/state, and legacy system power |
| HPE iLO Controller | Firmware, name/type, UUID, state, and legacy license property where present |
| HPE Fan (iLO 4) | Legacy FanName, CurrentReading, Units, Oem.Hp location, and state |
| HPE Fan (iLO 5-7) | Modern Name, Reading, ReadingUnits, Oem.Hpe location, and state |
| HPE Temperature Sensor | Name, temperature, state, physical context, thresholds, and optional legacy number/units |
| HPE Power Supply | Inventory, serial, health/state, input voltage, output watts, and optional legacy OEM properties |
| HPE System Power (iLO 5-7) | PowerControl member identity, capacity, consumption, and average/minimum/maximum watts where available |

The live reference inventory contained one server, one controller, seven legacy fans, 37 temperature sensors, two power supplies, and one adapter instance. The two modern-only object types produced no objects on that system.

This design uses parallel legacy and modern mappings, not negotiated generation detection. Missing identities can cause records to be skipped with warnings. Temperature identity now uses sensor name rather than sensor number; fans use generation-specific object type names. Server/controller identity uses UUID, power supplies use serial number, and modern system power uses MemberId. Builder also separates configured sources using adapter_instance_id.

Health and state are properties, not custom alerts. Powered-off temperature values of zero with Offline state are not actual 0 C measurements. Zero thresholds and Absent/Warning power-supply records need context and do not independently establish hardware faults.

## Before importing

- Use dedicated credentials with permission for the required Redfish reads; the minimum iLO role was not independently validated.
- Confirm collector DNS and HTTPS connectivity, normally port 443.
- Use a trusted certificate whose SAN matches the configured hostname or address, with TLS verification enabled.
- The reviewed export has a blank hostname, TLS default Verify, and credential references rather than stored credentials.
- Back up your existing design and plan a maintenance window if replacing an installation.

## Connection and requests

Use HTTPS, Basic authentication, and base path `redfish/v1` without a leading slash. Session authentication is disabled. Headers are the generated Basic Authorization value, `Content-Type: application/json`, and `Connection: close`.

| Purpose | Method and full path |
| --- | --- |
| Source test and Server | GET `/redfish/v1/Systems/1/` |
| Thermal | GET `/redfish/v1/Chassis/1/Thermal/` |
| Power | GET `/redfish/v1/Chassis/1/Power/` |
| iLO Controller | GET `/redfish/v1/Managers/1/` |

All requests are read-only. Pagination is disabled and resource ID `1` is fixed. The selected modern mockups retain these endpoints, but other resource IDs, schemas, permissions, or firmware may require edits. No power-control, firmware-update, or configuration actions are included.

## Import and configure

1. Download the JSON and review this guide. Use a distinct staging name if the original design already exists; Builder rejected same-name imports in the tested environment.
2. Open **Build > Developer Center > Management Pack Builder > Import**.
3. Configure source host, collector, HTTPS port, credentials, and certificate verification.
4. Test the source and every request; compare returned fields with the mappings.
5. Run **Verify > Perform Collection**. Inspect logs and actual inventory, not just the success badge.
6. Install through Builder only after reviewing the results for your device.
7. In **Integrations**, add the runtime account separately. Builder source credentials are not runtime account credentials.
8. Validate the runtime account and check at least two scheduled cycles, fresh timestamps, inventory, and readings before relying on monitoring.

### Replacing an existing installation

**This is not a verified non-destructive upgrade.** The lab replacement used a separately tested draft, explicitly approved uninstall of the old pack, retention of its Builder design as a legacy backup, renaming of the tested draft to HPE iLO Redfish, re-verification, and installation. The generated pack identity changed. Changed temperature identifiers and fan type names also mean historical object continuity must not be assumed.

**VCF's uninstall warning states that all associated data, metadata, and supplied content will be deleted and the removed pack cannot be recovered through that operation.** Do not uninstall casually to resolve a name conflict. Preserve required data/configuration using your organization's backup process and obtain explicit approval before choosing this destructive replacement workflow. A design JSON backup does not preserve collected history. Runtime accounts must be recreated after removal.

## Troubleshooting

- A successful collection badge can coexist with missing records. Check expected inventory and warnings.
- On the tested iLO 4, eight warnings for missing modern fan/power identifiers were expected and the legacy inventory remained present. Do not dismiss warnings for server, controller, temperature, PSU, or the fan mapping expected on your generation.
- Some Gen12 mockup PSU records lack serial-number identities and may be omitted by this design. Offline field presence is not proof of collection.
- Failed-to-respond errors on the reference iLO improved with `Connection: close`. Retest after header changes.
- TLS name mismatch: use a certificate matching the configured endpoint and correct trust/DNS. The lab used explicitly approved No Verify after a name mismatch; this retains encryption but disables server identity verification. The public default remains Verify. Do not switch to HTTP.
- 401/403: check the runtime or source credentials and Redfish permissions separately.
- Zero sensor readings: inspect power state and sensor state before interpreting values.

## Limitations

- No claim of universal compatibility with all iLO generations, firmware, or hardware. iLO 5–7 remains unverified on hardware.
- The modern fan/power definitions were not exercised with live modern data. The offline audit covered three iLO 5, one iLO 6, and three Gen12/iLO 7 mockups.
- Optional legacy fields may be absent on modern systems: temperature number/units, OEM power-supply fields, processor health rollup, and license edition. Missing values are not zero or healthy.
- No individual disk, RAID/storage-controller, DIMM, or CPU objects.
- No custom dashboards, alerts, event mappings, or server-to-component topology. Observed relationships were Builder defaults.
- Powered-on fan, temperature, and power behavior and sustained scheduled runtime collection remain unverified.

## Security

Do not publish credentials, raw responses, private addresses, hostnames, or device identifiers in issues or screenshots. Use HTTPS with certificate verification and dedicated credentials. See the repository [security guidance](../SECURITY.md).
