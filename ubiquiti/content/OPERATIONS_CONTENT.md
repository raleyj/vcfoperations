# UniFi Operations content specification

Management Pack Builder does not embed dashboards, symptoms, alerts, recommendations, policies, views, or reports in this JSON design. Build and export this content separately after the resource model and scheduled collection pass the required live validation. This is a future content plan; PoE mappings and finished dashboards/alerts are not included in the August 31 tested export.

## Dashboard: UniFi site operations

- Site selector and collection-status context.
- Device totals grouped by `ONLINE`, `OFFLINE`, transitional, and unknown states.
- Devices with stale collection timestamps, using platform collection statistics rather than a duplicate API metric.
- CPU and memory utilization for online devices, with unknown values excluded from numeric rollups.
- Device uptime and recent reset candidates.
- Uplink raw rates, clearly labeled as unconverted until rate semantics are confirmed.
- WAN inventory and port-state summaries only after the relevant objects are validated.

## Dashboard: UniFi device drill-down

- Identity, model, firmware, IP address, MAC address, support state, and parent site.
- CPU, memory, load averages, uptime, and uplink raw rates.
- Child port list with link state, connector, maximum/negotiated speed, and PoE state.
- Collection health displayed separately from device health.

## Initial symptoms and alerts

| Condition | Persistence and recovery | Scope and guardrails |
|---|---|---|
| Device state is `OFFLINE` | Require multiple consecutive collections; clear only after a sustained `ONLINE` state | Suppress during maintenance. Do not trigger when the adapter or site request failed. |
| Device CPU or memory is high | Warning and critical persistence thresholds defined by policy; clear below a lower recovery threshold | Evaluate only numeric readings from online devices. Start disabled until baseline data is reviewed. |
| Device uptime reset | Detect a significant drop between valid samples | Informational reboot indicator, not a negative-rate alarm. Ignore missing/stale samples. |
| Expected port changes from `UP` | Require persistence; clear on stable `UP` | Enable only for operator-designated expected/uplink ports. An unused or administratively disabled port must not alert by default. |
| PoE state becomes `LIMITED` | Require consecutive readings; clear when `UP` or intentionally disabled | Do not treat absent PoE data as `DOWN`. |
| Collection/account failure | Use platform adapter/account status and request diagnostics | One collection alert should suppress child device/port floods. Never include credentials in alert text. |

## Recommendations

Each alert should include the affected site/device/port, current state, last successful collection time, and the next safe diagnostic step. Recommendations remain read-only; no port, PoE, gateway, or firmware action is included.

## Release gates

- Simulated fixture faults associate with the intended component and parent.
- A controller/API outage creates one collection-focused condition rather than many device conditions.
- Missing, null, stale, offline, and numeric zero remain distinct.
- Alerts clear after recovery and honor maintenance suppression.
- Dashboard object counts and query times remain acceptable at the validated scale.
