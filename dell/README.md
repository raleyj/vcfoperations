# Dell iDRAC Redfish

A community Management Pack Builder design for direct PowerEdge monitoring through iDRAC over HTTPS. OpenManage Enterprise, OMEVV, and a bridge appliance are not required by this design.

- [Builder design JSON](designs/Dell%20iDRAC%20Redfish.json)
- [Project walkthrough](blog/README.md)

Exported design version: **1.0.0**. Import the JSON into Builder; it is not an installable `.pak`. The exported design is preserved byte for byte. Its hostname default is empty and its TLS default is **Verify**. Credentials must be supplied separately.

## Tested environment and status

- PowerEdge R650 with iDRAC9 Datacenter and firmware 7.20.30.00.
- VCF Operations 9.1.0.0400.25541561, built-in Management Pack Builder.
- Reference server powered off during testing.
- Source connection, full Builder collection, and installation succeeded on August 27, 2026.
- Test collection returned **9 objects, 27 metrics, 58 properties, 8 default relationships, and 0 events**. Totals include Builder's adapter instance and default collection statistics.
- Runtime integration-account validation and sustained scheduled collection were **not verified in this project**.

This is a custom community preview, not a Dell or Broadcom certified management pack. Other iDRAC generations, firmware versions, and PowerEdge models need separate validation.

## Coverage

| Object type | Coverage |
| --- | --- |
| Dell PowerEdge Server | Hostname, service tag, UUID, model, BIOS, installed memory, processor counts and model, power state, and available health rollups |
| Dell System Power | Consumed, allocated, and capacity watts; average, minimum, and maximum consumption |
| Dell Power Supply | Identity, model, firmware, serial number, state, redundancy status, efficiency, input/output power, and capacity |
| Dell Temperature Sensor | Sensor identity and context, Celsius reading, health/state, and available warning/critical temperature thresholds |

The reference inventory was one server, one system-power object, two power supplies, four temperature sensors, and one adapter instance. Builder adds `adapter_instance_id` to object identity to separate different configured sources. Power-supply identity also uses member ID and serial number; server identity uses UUID; temperature identity uses sensor number.

Health values are string properties. Unknown or null health is not normalized to healthy. Null numeric readings are omitted, not converted to zero. In the powered-off test, inlet temperature was 20 C and total standby power was 26 W; CPU temperature readings were absent.

## Connection and requests

Use HTTPS on the iDRAC management port, normally 443, with Basic authentication. Enter the ordinary iDRAC username and password in the credential fields; do not apply the QNAP password encoding procedure. The client constructs the authentication header. Session authentication is disabled.

Base path: `redfish/v1` (Builder adds the separating slash).

| Purpose | Method and full path |
| --- | --- |
| Source connection test | GET `/redfish/v1/` |
| Server | GET `/redfish/v1/Systems/System.Embedded.1` |
| Power | GET `/redfish/v1/Chassis/System.Embedded.1/Power` |
| Thermal | GET `/redfish/v1/Chassis/System.Embedded.1/Thermal` |

All configured API requests are GET requests. No power-control, firmware-update, or configuration actions are included. Pagination is disabled for these singleton resources. The `System.Embedded.1` resource paths are fixed to the tested layout and must be checked on other systems.

## Import and configure

1. Download the JSON. If using the design ZIP, extract it first. Preserve existing designs and use a separate test copy where needed.
2. In VCF Operations 9.1, open **Build > Developer Center > Management Pack Builder > Import** and select the JSON.
3. Configure Source with the collector, your iDRAC hostname, HTTPS port, and dedicated account credentials. Prefer a least-privilege account with access to the required Redfish reads. The minimum role was not independently validated in this project.
4. Keep TLS verification enabled. Install/trust the appropriate certificate chain and use a hostname or IP address present in its SAN. Confirm the collector, not just your workstation, can resolve that hostname and reach the management port.
5. Run the source connection test. Confirm valid Redfish JSON is returned. Run each collection request and compare the response with the mappings.
6. Run **Verify > Perform Collection**. Inspect actual objects, readings, identities, and missing values.
7. Install the validated management pack through Builder.
8. Open **Integrations**, locate **Dell iDRAC Redfish**, and add an account with its own host, collector, TLS configuration, username, and password. Builder test credentials are not copied into the runtime account.
9. Validate the account, then verify at least two scheduled collection cycles, fresh timestamps, and plausible values against iDRAC before relying on monitoring.

## TLS troubleshooting

In the lab, accepting the self-signed certificate did not fix its name mismatch: the certificate covered an iDRAC hostname, while the connection used an IP address. The workstation could resolve the certificate's hostname, but the Operations collector could not. Testing proceeded with explicit approval to use **No Verify** for that lab source.

No Verify keeps encryption but disables certificate identity verification. It is not the recommended deployment setting. The public design defaults to Verify; fix DNS, trust, and certificate naming for your environment. Do not switch to unencrypted HTTP to resolve this issue.

## Limitations

- No fan metrics: the powered-off reference returned an empty fan list. Adding fan mappings requires another test with real fan data.
- No individual disk, RAID, storage-controller, DIMM, or CPU objects; server health rollups are not detailed component monitoring.
- No custom dashboards, alert definitions, event mappings, or custom server-to-component topology. The eight test relationships were Builder defaults.
- Temperature and power units are explicit in labels; the Builder unit list did not offer Celsius or watts. Efficiency uses percent and installed memory uses GiBy.
- Dell marks the tested `/Power` and `/Thermal` resources deprecated in favor of newer subsystem resources. They worked on the tested firmware; migration to newer endpoints needs validation.
- The release is design JSON, not a standalone `.pak`. Do not rename JSON or ZIP files to `.pak`.
- Installation and a successful test collection do not prove continuous runtime collection.

Do not publish credentials, raw response bodies, private addresses, hostnames, service tags, or serial numbers in issues or screenshots. See the repository [security guidance](../SECURITY.md).
