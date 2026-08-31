# Ubiquiti UniFi Network

A community Management Pack Builder design for direct HTTPS collection from the local UniFi Network API. No bridge appliance is required.

## Downloads

- [Current Builder design JSON](designs/Ubiquiti%20UniFi%20Network.json)
- [Original August 27 release](https://github.com/raleyj/vcfoperations/releases/tag/unifi-v1.0.0)

Current revision: **August 31, 2026**. The Builder export still reports version **1.0.0**; the date and Git commit distinguish this expanded revision. This JSON is a Builder design, not an installable `.pak`. The original release remains available for rollback. The earlier generated 1.1 candidate is not the live-tested export published here.

## Tested environment and status

Recorded lab platform: **UDM Pro**, **UniFi OS 5.1.29 (Early Access)**, **UniFi Network 10.5.67 (Official)**, and **VCF Operations 9.1.0.0400.25541561**.

On August 31, the existing design was extended in place and passed two full Builder collections. Both returned **159 objects**, **959 properties**, and **315 relationships**; metric values returned were **219** and **214**. These totals include Builder default objects/relationships and are lab observations, not fixed expected counts. Missing optional readings can change metric counts.

The in-place upgrade completed successfully as installed management pack **1.0.0.2**. The existing account was preserved and showed **Collecting** afterward. Two scheduled cycles and sustained runtime collection still need separate verification. A Builder success badge does not prove scheduled collection. See [compatibility and validation](COMPATIBILITY.md).

This is a community integration, not an official Ubiquiti or Broadcom-supported management pack. Other versions, devices and hosting layouts require testing.

## Coverage

| Object type | Coverage |
| --- | --- |
| UniFi Site | Site ID, internal reference and name |
| UniFi Device | Existing identity, model, firmware/state, uptime, CPU/memory, load averages and uplink rates |
| UniFi Port | Site/device IDs, port index, link state, connector, maximum and negotiated speed |
| UniFi WAN Interface | Site ID, WAN ID and name |

Four custom object types, ten numeric metric definitions (eight device plus two port speed metrics), and three explicit relationships: Site-to-Device, Device-to-Port and Site-to-WAN.

Port speed units are **MBit/s** and labels include Mbps. A down port can retain a speed reading; consult Link State before interpreting it as active. Port identity combines Site ID, Device ID and Port Index, not the API response row index. Device-to-Port matching combines device and site IDs. Builder also scopes object identity to its adapter instance.

## Before importing

- Use a collector with HTTPS connectivity to the UniFi OS console.
- Prepare a local Network integration API key with the least access available for these GET requests.
- Use a trusted certificate matching the console hostname. The export defaults to TLS Verify and port 443.
- Keep a copy of the existing design and document the runtime account before upgrading.

## Connection and requests

Authentication uses `X-API-KEY: ${authentication.credentials.api_key}`. Enter the key in the protected credential field, not in the JSON. The hostname default is blank.

All paths below are relative to `/proxy/network/integration/v1`:

| Request | GET path |
| --- | --- |
| Application Info | `/info` |
| Sites | `/sites` |
| Devices | `/sites/${requestParameters.siteid}/devices` |
| Latest Device Statistics | `/sites/${requestParameters.siteid}/devices/${requestParameters.deviceid}/statistics/latest` |
| Device Details and Ports | `/sites/${requestParameters.siteid}/devices/${requestParameters.deviceid}` |
| WAN Interfaces | `/sites/${requestParameters.siteid}/wans` |

Sites, Devices and WAN Interfaces use offset/limit paging with a page size of 100. Device detail is not paged. Preserve all chained parameters and expressions. WAN paging passed a live Builder test with two WAN records; this does not establish large-inventory scale.

## Import and configure

1. Import the JSON into **Build > Developer Center > Management Pack Builder**.
2. Builder rejects duplicate design names. For an existing installation, preserve the existing design/account and use Builder's edit/verify/Upgrade workflow. Importing a renamed copy is a separate design, not an in-place update.
3. Configure the Source hostname, port, collector and protected API Key.
4. Test Application Info, Sites, Devices, Statistics, Device Details and Ports, and WAN Interfaces.
5. Run a full collection. Inspect representative identities, parent-child relationships, port state/speed, and WAN names.
6. Install a new design or use **Upgrade** for changes to the existing installed design.
7. Check the runtime integration account independently. Verify at least two scheduled cycles, recent timestamps and plausible values against UniFi.
8. Validate missing optional data, offline devices, pagination, failure isolation and recovery before relying on the pack operationally.

The lab Source test currently used No Verify. That does not change the public export's Verify default, and certificate trust remains a deployment requirement.

## Troubleshooting

- **401/403:** refresh the local API key and check permissions. Source credentials and runtime account credentials are separate.
- **404:** compare the installed Network application's local API documentation and hosting prefix.
- **TLS failure:** fix certificate trust and hostname matching; do not make No Verify the production default.
- **No objects:** check site visibility, adopted devices, paging and chained parameters.
- **Port speed on a down port:** the API can retain speed; consult Link State.
- **Builder works, runtime fails:** check runtime credentials and collector connectivity separately.

## Limitations

- No port traffic/errors/discards, PoE properties or power consumption, WAN health/failover/performance, or events are mapped in this live-tested revision.
- Uplink TX/RX rates remain unconverted raw API values. Their bits-versus-bytes semantics still require controlled validation.
- Dashboards, symptoms, alerts and policies are not shipped. The [content specification](content/OPERATIONS_CONTENT.md) is a plan, not an importable content pack.
- No universal UDM-version support claim, large-scale test, outage/fault-injection test, scheduled-cycle evidence or soak test is claimed.
- Preserving design/object keys does not itself prove historical data continuity after upgrade.

## Security

Do not publish API keys, raw collection logs/responses, private addresses, hostnames or device identifiers. The exported hostname is blank and API key remains a protected credential reference. See [security guidance](../SECURITY.md).
