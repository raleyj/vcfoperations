# Dell iDRAC operational content specification

This specification records the operational-content design. The Dell-scoped dashboard, server-health symptom, recommendation, and two-cycle server-health alert are deployed in VCF Operations. Live alarm activation/recovery and the broader component policies were not forced because no additional hardware or disruptive test window is available; they are documented best-effort limitations rather than open roadmap gates.

## Server overview

Show server name, power state, overall health, CPU/memory/storage/cooling/power-supply rollups, current and peak power, hottest temperature, fan count, and data age. The view must display unavailable readings as `Unknown`; it must not substitute zero.

## Component drill-down

Group components by power supplies, temperature sensors, fans, storage, memory, and processors. Show raw health/state properties, current reading and unit, and collection freshness. Do not infer a failed absent component from an empty optional collection.

## Alert policies

| Condition | Trigger | Recovery | Guardrails |
|---|---|---|---|
| Collection stale | Data age exceeds two collection intervals | Two consecutive current collections | Suppress component alarms while collection is stale |
| Server health | Raw health is Warning or Critical for two cycles | Raw health is OK for two cycles | Unknown is not OK and is not Critical |
| Temperature | Reading exceeds the source threshold for two cycles | Below threshold for two cycles | Missing/null never becomes zero |
| Fan health | Fan raw health is Warning/Critical or RPM violates a source threshold | Healthy for two cycles | Do not invent a universal RPM threshold |
| Supply health | Installed supply raw health is Warning/Critical for two cycles | Healthy for two cycles | Absent optional supply is not failed |
| Storage rollup | Storage rollup is Warning/Critical for two cycles | OK for two cycles | Use component detail when available |

## Identity and topology

Use the server UUID as the server identity. Use source-scoped `MemberId` for replaceable components and retain serial number as a property, not as the sole identity. Create server-to-component relationships only when the Builder can map a stable shared source key; do not use a cross-product relationship.

## Release acceptance

Before publishing a Builder export, verify a clean import, upgrade over the prior version, rollback from the saved prior export, unchanged server/component identifiers, expected object counts, and version-matched documentation. Remove credentials, endpoint addresses, service tags, serial numbers, and live response samples from public fixtures.
