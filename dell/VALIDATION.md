# Dell iDRAC management pack validation

## Operational content test - 3 September 2026

- All nine legacy semantic regression tests passed. They cover powered-off null readings, true zero values, empty and missing optional collections, partial Thermal responses, stable fan identity, additive schema changes, missing `MemberId` fallback, and preservation of raw health.
- All nine experimental modern-framework tests and all three Redfish probe URL-safety tests passed. These remain synthetic tests and do not establish compatibility with untested iDRAC hardware.
- The installed adapter is actively populating VCF Operations inventory. The live tested Dell server object reported Health 100%, BIOS 1.17.2, CPU Health OK, and Cooling Health OK.
- Component inventory persisted in VCF Operations with 16 fans, four temperature sensors, two power supplies, two processors, eight populated memory modules, three storage resources, and the expanded firmware inventory visible under their Dell object types.
- The live server object showed no active alerts during this healthy-state check. No false low-temperature alarm was observed.
- No disruptive hardware fault was introduced. Fault persistence, maintenance suppression, collection-stale behavior, and recovery therefore remain unverified limitations rather than open roadmap requirements.

## Operational content deployment - 3 September 2026

- Deployed the user-defined `Dell server health is not OK` property symptom for the `Dell PowerEdge Server` object type. It evaluates `Status Health Rollup` as not equal to `OK` with Warning criticality.
- Deployed the user-defined `Dell iDRAC Operations` dashboard with Object List, Property List, Metric Chart, and Alert List widgets. VCF Operations assigned dashboard tab ID `d3d0dad3-5537-4b20-b5ed-51a043e4a036`, and the dashboard was reopened successfully after saving.
- Scoped the dashboard Object List to all 66 objects supplied by the `Dell iDRAC Redfish` adapter. Self Provider and automatic first-row selection are enabled. A live check showed the tested Dell server, the expected Dell count, and no non-Dell infrastructure-health object in the list.
- Deployed the `Dell server health degraded` alert definition for `Dell PowerEdge Server`. It uses the deployed symptom, affects Health, includes the operator recommendation, and requires two cycles to raise and two cycles to clear.
- The healthy server produced no active Dell health alert and no false low-temperature condition. Widget interaction drill-down and fault raise/clear behavior were not proven with a disruptive live fault and are documented as limitations.

## Firmware inventory expansion - 3 September 2026

- Added the read-only Redfish request `UpdateService/FirmwareInventory?$expand=*($levels=1)` to the live VCF Operations 9.1 Builder design.
- Added the `Dell Firmware Component` object type with firmware inventory ID, component name, release date, health/state, updateable flag, and version fields.
- Live collection against the tested PowerEdge R650 with iDRAC9 7.20.30.00 completed successfully in 8 seconds: 65 objects, 125 metrics, 463 properties, and 64 relationships.
- No firmware update, power control, credential, TLS, or event mutation actions were introduced.
- The management pack upgrade completed successfully and VCF Operations reported the updated pack as installed.

## Tested configuration

- VCF Operations 9.1 Management Pack Builder
- Dell PowerEdge R650
- iDRAC9 firmware 7.20.30.00
- Validation date: 2 September 2026

## Completed evidence

The powered-on iDRAC UI and a fresh Builder collection were compared during the same validation session. CPU temperatures, inlet and exhaust temperatures, current system power, and peak power agreed within normal sampling drift. The Builder collection completed successfully in zero reported seconds with 25 objects, 55 metrics, 186 properties, and 24 relationships.

The design now discovers 16 individual fan objects from the legacy Thermal response. Each fan has source-scoped identity fields, location and health properties, units, and one Fan Speed RPM metric. A representative fan collected 8,160 RPM, matching the powered-on iDRAC cooling view during the session.

Earlier powered-off collection evidence retained the server and component inventory while unavailable CPU and exhaust readings were absent rather than converted into low numeric values. The deployed server-health policy now provides two-cycle persistence and recovery configuration; live fault activation and clearing were not forced.

The updated design was verified twice after the fan and description changes. VCF Operations then reported the management pack upgrade as successfully installed.

On 3 September 2026, nine sanitized legacy semantic regressions passed for powered-off null values, true zero values, empty and missing optional collections, partial Thermal responses, fan replacement identity, additive schema changes, missing MemberId fallback, and raw health preservation. The separate modern/iDRAC10 framework also passed its existing nine local tests. These are fixture results and do not establish compatibility with untested hardware.

The operational dashboard and server-health alert are deployed. `OPERATIONS_CONTENT.md` records the broader design for data age, collection-stale suppression, unknown states, source thresholds, and component identity. Behaviors that require a disruptive fault or additional hardware remain unverified best-effort limitations.

On 3 September 2026, the live Builder design added expanded Processor, Memory, and Storage requests using `$expand=*($levels=1)`. The tested R650 returned two processors, eight populated memory modules, and three storage resources. New Dell Processor, Dell Memory Module, and Dell Storage Resource object types were added. Verification completed successfully in one second with 38 objects, 97 metrics, 274 properties, and 37 relationships. VCF Operations then reported the upgraded management pack as successfully installed.

## Best-effort closure

No additional iDRAC hardware will be available in this lab. Controlled authentication/TLS failures, destructive power transitions, maintenance suppression, live fault raise/clear, multi-source identity, physical component replacement, server-to-component relationships without a stable Builder key, deeper controller/drive/volume discovery, other PowerEdge models, other iDRAC generations, and modern endpoint compatibility are closed as best-effort limitations and are not open roadmap requirements. Synthetic fixtures exercise several alternate shapes, but they do not establish live compatibility. The separate iDRAC10 framework remains repository-only and untested on physical iDRAC10 hardware.
