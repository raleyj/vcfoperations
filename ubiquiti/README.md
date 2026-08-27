# Ubiquiti UniFi Network

A community Builder design using the local UniFi Network integration API. No bridge appliance is required.

## Downloads

- [Builder design JSON](designs/Ubiquiti%20UniFi%20Network.json)
- [Version 1.0.0 release and design ZIP](https://github.com/raleyj/vcfoperations/releases/tag/unifi-v1.0.0)

Exported design version: **1.0.0**. This is a Builder design, not an installable `.pak`. The export is preserved unchanged. The release ZIP includes the guide as it stood when released; this README is the current guide.

## Tested environment and status

The export originates from VCF Operations **9.1.0.0400.25541561** and targets the UniFi OS proxy prefix `/proxy/network/integration/v1`. The source Builder listed it as Verified and Installed during publication on August 27, 2026.

A specific tested console model and Network application version are not recorded in the published design/guide. Do not infer support for all versions or hosting layouts; check the destination application's local API documentation.

This documentation review does not perform a new import, installation, or scheduled-collection test. Sustained runtime collection is not established by the Builder status. This is a community integration, not a Ubiquiti or Broadcom certified management pack.

## Coverage

| Object type | Coverage |
| --- | --- |
| UniFi Site | Site ID, internal reference, and name |
| UniFi Device | Identity, model, firmware/state, CPU and memory utilization, uptime, load averages, and uplink statistics |

The design defines two custom object types, eight device metrics, and a site-to-device relationship. Counts of discovered sites and devices depend on the destination.

## Before importing

- Choose a collector that can reach the UniFi OS console over HTTPS.
- Prepare a local Network integration API key with the least privileges available for the required GET requests. Do not substitute a UI password or unrelated cloud credential.
- Use a trusted certificate matching the console hostname. The design defaults to port 443 and TLS Verify.

## Connection and requests

The source sends a local Network API key in `X-API-KEY` through a credential reference. The hostname default is blank, port defaults to 443, and TLS defaults to Verify.

| Purpose | Method and path |
| --- | --- |
| Application info / source test | GET `/proxy/network/integration/v1/info` |
| Sites | GET `/proxy/network/integration/v1/sites` |
| Devices | GET `/proxy/network/integration/v1/sites/${requestParameters.siteid}/devices` |
| Latest device statistics | GET `/proxy/network/integration/v1/sites/${requestParameters.siteid}/devices/${requestParameters.deviceid}/statistics/latest` |

Sites feeds the site parameter into Devices, which feeds the device parameter into Statistics. Preserve the offset/limit paging and chained parameters. All four collection requests are GET requests.

## Import and configure

1. Extract the design ZIP if using a release archive. Import the JSON into **Build > Developer Center > Management Pack Builder**. It is not an installable `.pak`.
2. Preserve any existing design and use a distinct name for your test copy.
3. Open Source. Supply the console hostname (without a URL scheme or path), port, collector, and API Key through the UI.
4. Leave the `X-API-KEY` credential expression intact. Do not replace it with a literal key in the design.
5. Test Application Info at `/proxy/network/integration/v1/info`.
6. Validate Sites, Devices, and Latest Device Statistics in dependency order. Preserve the site/device request parameters and offset/limit paging.
7. Run a full collection. Inspect site/device inventory, relationships, and available statistics; counts depend on your environment.
8. Install through Builder. Configure the installed integration account separately with the host, API key, TLS settings, port, and collector.
9. Verify at least two scheduled collection cycles, recent timestamps, and plausible values against UniFi.

## Troubleshooting

- 401/403: verify the local API key, permissions, target Network application, and absence of whitespace in the credential.
- 404: check the Network API version and hosting layout against its local API documentation.
- TLS errors: fix certificate trust and hostname matching; do not publish a design defaulting to No Verify.
- No objects: check site visibility, adopted devices, paging, and chained request parameters.
- Builder succeeds but runtime fails: check runtime-account credentials and collector connectivity independently.

## Limitations

- Per-port metrics, dedicated WAN monitoring, and events are not included.
- Uplink rates retain raw API values without a configured unit conversion.
- The UniFi OS proxy prefix may not apply to other hosting layouts.
- Available objects and statistics depend on local API version, site visibility, and adopted devices.
- A successful Builder test or installation does not prove continuous runtime collection.

## Security

Do not publish credentials, raw response bodies, private addresses, hostnames, or device identifiers in issues or screenshots. See the repository [security guidance](../SECURITY.md).

Keep the literal API key out of the JSON. Enter it in the protected credential fields, and preserve the `X-API-KEY` expression.
