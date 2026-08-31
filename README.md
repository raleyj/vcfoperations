# VCF Operations Management Pack Designs

Community management pack designs for collecting QNAP, Ubiquiti UniFi, Dell iDRAC, and HPE iLO data directly into VMware Cloud Foundation Operations. These designs do not require a bridge appliance.

Choose an integration below for its design download, setup guide, tested scope, and limitations. Shared validation and packaging instructions are in [tools](tools/README.md).

| Integration | Setup and coverage |
| --- | --- |
| QNAP Direct HTTPS | [QNAP guide](qnap/README.md): array, disk health, volume usage, and iSCSI service inventory |
| Ubiquiti UniFi Network | [UniFi guide](ubiquiti/README.md): sites, devices, device statistics, and site-to-device relationships |
| Dell iDRAC Redfish | [Dell guide](dell/README.md): PowerEdge health and inventory, system power, power supplies, and temperatures |
| HPE iLO Redfish | [HPE guide](hpe/README.md): ProLiant inventory, controller details, fans, temperatures, and power; August 31 best-effort iLO 4–7 update (iLO 4 tested live; newer hardware unverified) |

## Start here

Each integration folder uses the same layout: `README.md` for its complete guide and `designs/` for its Builder JSON. The guides use matching sections for downloads, tested status, coverage, prerequisites, requests, installation, troubleshooting, limitations, and security. Device coverage and credentials remain specific to each integration; a missing compatibility result is recorded as unknown rather than assumed.

The Dell walkthrough is consolidated into its guide; no separate blog folder is needed. QNAP and UniFi have published version 1.0.0 download releases. Dell and HPE currently provide their JSON directly. Existing release ZIPs retain their original documentation; the repository guides contain the latest documentation updates.

These downloads are **Management Pack Builder design JSON files, not installable `.pak` files**. Extract a design archive, import its JSON into Builder, configure your environment, validate collection, and install through Builder. Do not upload a design ZIP to a `.pak` installer.

The originating Operations build is **9.1.0.0400.25541561**. Other releases and device software versions require validation. These are community integrations; no vendor certification or support commitment is claimed.

1. Read the integration's guide and limitations.
2. Import its JSON under **Build > Developer Center > Management Pack Builder**. Preserve existing designs; use a distinct name for a test copy.
3. Configure the source with your host, collector, and credentials. Keep TLS certificate verification enabled.
4. Test the connection and run a full Builder collection. Review the returned inventory and values.
5. Install through Builder, then configure the installed integration account separately.
6. Verify scheduled collection and recent timestamps in your environment.

Builder test credentials are separate from runtime integration-account credentials. An installed status alone does not prove that scheduled collection is working.

## Security and contributions

Never commit credentials, encoded passwords, session IDs, test-response bodies, or private inventory. See [SECURITY.md](SECURITY.md). Preserve structural Builder IDs and request expressions when editing designs.

Include the Operations version, device software version, reproduction steps, and sanitized error text when reporting a problem. Do not attach raw collection logs or full environment exports to public issues.

## License

This repository uses the existing GPL-3.0 license in [LICENSE](LICENSE). Product names and trademarks belong to their respective owners.

