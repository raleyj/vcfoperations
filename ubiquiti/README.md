# Ubiquiti UniFi Network

A community Builder design using the local UniFi Network integration API. No bridge appliance is required.

Design: [Ubiquiti UniFi Network.json](designs/Ubiquiti%20UniFi%20Network.json).

Exported design version: **1.0.0**.

## Compatibility and scope

The export originates from VCF Operations 9.1.0.0400.25541561. It targets the UniFi OS proxy prefix `/proxy/network/integration/v1`. Check your Network application's local integration API documentation before using another hosting layout or software version.

The design includes UniFi Site and UniFi Device objects, site-to-device relationships, and device CPU, memory, uptime, load-average, and uplink statistics. Per-port metrics, dedicated WAN monitoring, and events are not included. Uplink rates retain raw API values without a configured unit conversion.

## Before importing

- Choose a collector that can reach the UniFi OS console over HTTPS.
- Prepare a local Network integration API key with the least privileges available for the required GET requests. Do not substitute a UI password or unrelated cloud credential.
- Use a trusted certificate matching the console hostname. The design defaults to port 443 and TLS Verify.

## Import and configure

1. Extract the design ZIP if using a release archive. Import the JSON into **Build > Developer Center > Management Pack Builder**. It is not an installable `.pak`.
2. Preserve any existing design and use a distinct name for your test copy.
3. Open Source. Supply the console hostname (without a URL scheme or path), port, collector, and API Key through the UI.
4. Leave the `X-API-KEY` credential expression intact. Do not replace it with a literal key in the design.
5. Test Application Info at `/proxy/network/integration/v1/info`.
6. Validate Sites, Devices, and Latest Device Statistics in dependency order. Preserve the site/device request parameters and offset/limit paging.
7. Run a full collection. Inspect site/device inventory, relationships, and available statistics; counts depend on your environment.
8. Install through Builder. Configure the installed integration account separately with the host, API key, TLS settings, port, and collector.
9. Verify scheduled collection status, recent timestamps, and values against UniFi.

## Troubleshooting

- 401/403: verify the local API key, permissions, target Network application, and absence of whitespace in the credential.
- 404: check the Network API version and hosting layout against its local API documentation.
- TLS errors: fix certificate trust and hostname matching; do not publish a design defaulting to No Verify.
- No objects: check site visibility, adopted devices, paging, and chained request parameters.
- Builder succeeds but runtime fails: check runtime-account credentials and collector connectivity independently.

This publishing preparation does not perform a new import, installation, or scheduled-collection test.
