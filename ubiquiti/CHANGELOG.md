# Changelog

## August 31, 2026 — live-tested port and WAN revision

Builder metadata remains 1.0.0; identify this revision by date and Git commit.

- Extended the existing design in place, retaining original Site/Device definitions.
- Added live-tested Device Details and Ports and paged WAN Interfaces requests.
- Added UniFi Port and UniFi WAN Interface object types.
- Added maximum and negotiated port speed metrics with MBit/s units; port state and connector are properties.
- Added composite port identity and site-scoped Device-to-Port matching, plus Site-to-WAN relationships.
- Two Builder collections succeeded with 159 objects and 315 relationships, including default Builder objects/relationships.
- Completed the in-place upgrade as management pack 1.0.0.2. The existing account remains present and shows Collecting; two scheduled cycles and sustained runtime collection are separate gates.
- Public export retains blank hostname, protected credential references and TLS Verify.

This is the exact live-tested Builder export, not the earlier generated 1.1 candidate. PoE properties, port counters, WAN health/failover/performance, dashboards and alerts are not included. Raw uplink rate conversion and fault/scale/soak validation remain unfinished.

## Original release

The original design is preserved in the [unifi-v1.0.0 release](https://github.com/raleyj/vcfoperations/releases/tag/unifi-v1.0.0). Keep the existing account/history while validating an upgrade; uninstalling or deleting an account may lose data and is not the default rollback procedure.
