# Dell iDRAC VCF Operations Management Pack

## PowerEdge hardware visibility in VCF Operations

After building the QNAP integration, I wanted to bring Dell server hardware into VCF Operations without deploying OpenManage Enterprise. This custom management pack connects directly to iDRAC's Redfish API over HTTPS.

The first version covers server health and inventory, power consumption, power supplies, and temperatures. The Builder test passed and the management pack installed successfully. Ongoing collection from a configured integration account has not been verified as part of this project.

## The environment

I tested a PowerEdge R650 with iDRAC9 Datacenter, firmware 7.20.30.00, and VCF Operations 9.1.0.0400.25541561. The design was created with the built-in Management Pack Builder. The server was powered off during the test, which shaped the available sensor data.

This is a custom community preview. These results are not a compatibility matrix or a claim of Dell or Broadcom certification.

## How the management pack connects

**VCF Operations collector → HTTPS → iDRAC Redfish API**

There is no OpenManage Enterprise, OMEVV, exporter, or bridge in this design. The source uses Basic authentication with the iDRAC username and password. Unlike the QNAP pack, it does not require a manually Base64-encoded and URL-encoded password. Enter the ordinary password into the protected credential field and let the client construct the header.

All configured requests are GET requests. The pack does not invoke server power actions, change configuration, or update firmware. That describes the pack's behavior, not the privileges of the account used to connect. Use a dedicated account with the minimum access needed for these reads; I have not separately established the minimum iDRAC role.

## The Redfish requests

| Purpose | Method and path |
| --- | --- |
| Test the source | GET `/redfish/v1/` |
| Server inventory and health | GET `/redfish/v1/Systems/System.Embedded.1` |
| System power and power supplies | GET `/redfish/v1/Chassis/System.Embedded.1/Power` |
| Temperature sensors | GET `/redfish/v1/Chassis/System.Embedded.1/Thermal` |

The base path is `redfish/v1`; Builder supplies the slash between the host and path. The resource paths use the tested `System.Embedded.1` layout. Check them against your own iDRAC before assuming they apply unchanged.

Dell's responses mark Power and Thermal as deprecated in favor of newer subsystem resources. These endpoints worked on the tested firmware, but a future version should validate those newer resources rather than assuming the old ones will always remain available.

## The TLS issue that caught me out

The first connection reached iDRAC, but its self-signed certificate needed to be trusted. Accepting it was only the first step: the certificate named the iDRAC hostname, while the source was configured with an IP address.

Trusting a certificate does not make a hostname mismatch disappear. I tried the hostname in the certificate next. It resolved from the workstation, but the Operations collector could not resolve it.

That distinction is easy to miss when the browser already opens the iDRAC dashboard. The collector performs the API requests, so its DNS and network access are what matter.

For this lab test, I explicitly allowed No Verify for the source. HTTPS remained enabled, but certificate identity verification was disabled. For a deployment you intend to rely on, fix DNS and use a trusted certificate with a matching SAN. The exported design defaults to Verify and leaves the hostname blank.

## What the preview collects

The design contains four custom object types:

- **Dell PowerEdge Server:** hostname, model, service tag, UUID, BIOS, processor and memory inventory, power state, and health rollups.
- **Dell System Power:** consumed, allocated, and capacity watts, plus average, minimum, and maximum consumption.
- **Dell Power Supply:** identity, serial number, model, firmware, state, redundancy status, efficiency, and input/output power.
- **Dell Temperature Sensor:** identity, context, Celsius readings, health/state, and available warning and critical thresholds.

The full Builder test returned:

| Result | Count |
| --- | --- |
| Objects | 9 |
| Metrics | 27 |
| Properties | 58 |
| Default relationships | 8 |
| Events | 0 |

Those totals include the generated adapter instance and Builder's default statistics and relationships. The custom inventory consisted of one server, one system-power object, two power supplies, and four temperature sensors.

Builder adds an adapter instance identifier to object identities, so the same sensor number on different configured iDRACs remains distinct. Server identity uses UUID; power supplies also use member ID and serial number.

## A powered-off server still tells a useful story

The reference system reported 26 W of standby power and an inlet temperature of 20 C. It returned four temperature sensor objects, but CPU and exhaust temperature readings were null.

The numeric mappings correctly omitted unavailable readings rather than converting them to zero. A missing reading and a real zero mean different things. Health values remain string properties; Unknown or null is not treated as healthy.

The fan list was empty. I have not added pretend fan readings or claimed fan coverage. That work needs a powered-on test with actual fan data.

## Builder credentials and runtime credentials are separate

The same setup lesson from the QNAP project applies here: the credentials used to test a source in Builder are separate from the credentials on the installed integration account.

The pack installed successfully, but installation alone does not start a validated monitoring deployment. Add an account for the installed Dell iDRAC Redfish integration, provide its connection settings and credentials, validate it, and check scheduled collection and recent timestamps.

I have verified the Builder collection and installation for this version. I have not verified sustained scheduled collection, so this post does not claim that result.

## What is not included yet

- Fan readings, individual disk and RAID objects, DIMM objects, and CPU objects are not included.
- Health rollups provide summaries, not detailed component diagnostics.
- There are no custom dashboards, alert definitions, event mappings, or custom server-to-component topology relationships.
- Power and temperature units are stated in metric labels; the available Builder unit list did not include watts or Celsius. Efficiency uses percent and installed memory uses GiBy.
- Other PowerEdge models, iDRAC generations, and firmware releases need their own validation.
- No standalone `.pak` is supplied. The reusable artifact is an importable Builder design JSON.

## Deployment at a glance

1. Download the Dell design JSON from the repository. Extract it first if using the design ZIP.
2. Prepare a dedicated iDRAC account and verify collector-to-iDRAC HTTPS access, DNS, and certificate naming.
3. Import the JSON under **Build > Developer Center > Management Pack Builder**. Preserve any existing design.
4. Configure the test source with your iDRAC hostname, HTTPS port, collector, username, and ordinary password.
5. Test the source and collection requests, then run a full collection and compare values against iDRAC.
6. Install the validated management pack through Builder.
7. Add a separate integration account and validate its credentials and connection.
8. Confirm at least two scheduled collection cycles and fresh timestamps before relying on the data.

The ZIP is a distribution archive, not an installable management-pack package. Do not rename it to `.pak` or upload it to a conventional `.pak` installer.

## Final thoughts

This first version brings a useful set of PowerEdge hardware data into VCF Operations without another management appliance. The next areas to validate are powered-on fan data, the newer Redfish subsystem resources, and ongoing collection.

The troubleshooting lesson was straightforward: browser access does not prove collector access, trusting a certificate does not fix its name, and unavailable sensor data should stay unavailable.

## Explore the project

Get the design and deployment guide from [the Dell project on GitHub](https://github.com/raleyj/vcfoperations/tree/main/dell). Read the limitations and security guidance before deploying. The [QNAP walkthrough](https://justinraley.com/qnap-vcf-operations-management-pack/) covers the storage integration that preceded this work.
