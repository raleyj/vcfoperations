# QNAP Direct HTTPS

A community preview that collects directly from QNAP QTS over HTTPS. No SNMP bridge or OVA is required.

Design: [QNAP Direct HTTPS.json](designs/QNAP%20Direct%20HTTPS.json).

Exported design version: **1.0.0**. Its description still identifies preview limitations. The export is preserved unchanged, including defaults of two concurrent requests and two retries; validate collection behavior in your environment.

## Compatibility and scope

The existing project testing covered a QNAP TS-435XeU running QTS 5.2.9.3451 with VCF Operations 9.1.0.0400.25541561. This is not a compatibility guarantee for other hardware or firmware.

The design models array information, disk health, volume usage, and iSCSI service inventory. CPU utilization is currently a raw string property. Volume capacity values need unit and multi-volume validation. Fan mappings cover the tested hardware. Separate LUN/target objects, RAID groups, storage pools, IOPS, latency, dashboards, and alerts are outside the preview's scope.

## Before importing

- Provide collector connectivity to the NAS HTTPS management port; the default is 443.
- Use a trusted server certificate whose SAN matches the hostname supplied to the collector. Keep SSL Configuration set to Verify.
- Prepare a dedicated QTS account. Existing project tests required System Monitoring for system/disk/volume requests and System Management for the iSCSI request. **System Management grants broad management capabilities**; read-only shared-folder permissions do not make this a read-only system account. Review this permission requirement before deployment.

## Import and configure

1. Extract the design ZIP if using a release archive. Import the JSON into **Build > Developer Center > Management Pack Builder**. It is not an installable `.pak`.
2. Preserve any existing design and use a distinct name for your test copy.
3. Open Source and supply the collector, NAS hostname, HTTPS port, and credentials in the UI. Do not embed these values in the JSON.
4. URL-encode the QTS username for the Username credential.
5. For Encoded Password, Base64-encode the password's UTF-8 bytes, then URL-encode the Base64 result. Do not add a newline or encode twice. Generate this locally with a trusted tool, never an online encoder. The encoded value remains a password-equivalent secret.
6. Test session creation, the health request, and session release. Preserve the `authsid` session mapping.
7. Run a full Builder collection and compare inventory and values with QTS.
8. Install through Builder. Add/configure the installed integration account with its own host, collector, TLS settings, and correctly encoded credentials.
9. Verify at least two scheduled collection cycles, recent timestamps, and plausible values before relying on the integration. Compare coverage before retiring an existing bridge integration.

## Requests

| Purpose | Method and path |
| --- | --- |
| Login | POST `/cgi-bin/authLogin.cgi` |
| Health | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&sysHealth=1` |
| System statistics | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&hd=no&multicpu=1` |
| Disk health | GET `/cgi-bin/disk/qsmart.cgi?func=all_hd_data` |
| Volume usage | GET `/cgi-bin/management/chartReq.cgi?chart_func=disk_usage&disk_select=all&include=all` |
| iSCSI inventory | GET `/cgi-bin/disk/iscsi_portal_setting.cgi?func=get_all` |
| Logout | GET `/cgi-bin/authLogout.cgi` |

Authenticated requests include a session ID. Treat request URLs and logs as sensitive.

## Troubleshooting

- Missing `authSid`: inspect the login result and credential encoding. HTTP 200 alone does not prove authentication succeeded.
- Builder works but the integration account fails: enter the account credentials separately; they are not copied from Builder test settings.
- TLS errors: correct trust and hostname matching. No Verify removes server identity verification and is not the recommended deployment setting.
- Missing iSCSI data: check QTS permissions and firmware response shape. A zero LUN count is not proof that the NAS has no LUNs of any type.

This publishing preparation does not perform a new import, installation, or scheduled-collection test.
