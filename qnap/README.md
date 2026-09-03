# QNAP Direct HTTPS

Community QNAP QTS monitoring for VCF Operations 9.1 using direct HTTPS and the built-in Management Pack Builder.

## Downloads

- [Current Builder design](designs/QNAP%20Direct%20HTTPS.json)
- [Updated design bundle 1.1.1](qnap-direct-https-1.1.1-design.zip)
- [Update notes](RELEASE-NOTES-1.1.1.md)

The ZIP contains Builder JSON and documentation, **not an installable `.pak`**. Import the JSON into **Build > Developer Center > Management Pack Builder**, validate it, then install or upgrade through Builder. Bundle version 1.1.1 is a distribution revision; the tested installed integration reports **1.0.0.7**, and the exported design metadata retains version **1.0.0**.

## Tested environment

- QNAP TS-435XeU running QTS **5.2.9.3451**
- VCF Operations **9.1.0.0400.25541561**
- Two iSCSI targets and two LUNs

Other QNAP systems on the same QTS release may work if their endpoints, response structures, and permissions match. This is not a compatibility guarantee or QNAP/Broadcom certification. End users must validate their own model, firmware, and inventory.

## Coverage

| Object | Coverage |
| --- | --- |
| Array | Identity, firmware, memory, temperatures, fans, numeric CPU utilization |
| Disk | Identity, status, capacity, temperature, available SMART properties |
| Volume Usage | Existing Volume ID binding; total and free capacity in bytes |
| iSCSI Service | Settings and aggregate target, LUN, and initiator counts |
| iSCSI Target | Stable identity, status, mapped-LUN count |
| iSCSI LUN | Stable identity, status, mapping, thin state, sector size, capacity bytes |

The live Builder test returned **15 objects, 37 metrics, 84 properties, and 17 relationships** in two seconds. The in-place upgrade retained the account and existing volume identity.

## Completed observation and operational content

The minimum 24-hour scheduled observation completed with 287–288 LUN capacity samples and 288 samples for an inspected target status metric. Both LUNs reported Collecting and Data receiving; the inventory retained exactly two targets and two LUNs without duplicates.

The lab also has a **QNAP Storage Operations** dashboard, with QNAP-scoped inventory/collection status and alert history. Two user alert definitions were configured in the default policy:

- **QNAP Disk Temperature Is High:** Temperature C > 55, Warning.
- **QNAP iSCSI LUN Is Not Ready:** LUN Status Code != 0, Critical.

**Packaging boundary:** the dashboard, symptoms, recommendations, policy assignments, and Operations super metrics were configured separately in Operations. They are **not included in the Builder JSON or this ZIP**. Recreate or separately export/import that content for another deployment. Do not assume installing the design creates it.

## Resilience evidence and limits

On 3 September 2026, independent short-lived QTS sessions demonstrated:

- Explicit logout invalidated a session; a fresh login restored health access.
- A deliberate missing-endpoint HTTP 404 did not invalidate the same session's valid health request.
- An intentionally wrong password was rejected; the current password then authenticated successfully.
- The test client rejected the lab certificate under default trust and also when the certificate was trusted locally but the endpoint name did not match.
- Test sessions logged out cleanly, without touching the production adapter session.

These are **source-level checks**, not end-to-end VCF adapter fault injection. They do not prove automatic adapter retry during a mid-cycle failure, actual NAS password rotation, or how missing metrics propagate into Operations during a failed collection. A currently healthy adapter is not evidence of those failure paths.

## Credentials, permissions, and TLS

Use a dedicated QTS account. System Monitoring provided system/disk/volume access on the tested NAS; iSCSI required System Management, which grants broad management authority. Read-only shared-folder rights do not reduce that system role.

1. URL-encode the username.
2. Base64-encode the password's UTF-8 bytes, then URL-encode the Base64 result.
3. Enter the result in **Encoded Password**. Generate it locally; it remains a password-equivalent secret.

Builder test credentials and installed integration credentials are separate. Configure both where required. Keep **TLS Verify** enabled with a trusted certificate whose SAN matches the endpoint. The lab used HTTPS 443; QTS HTTP 8080 was not the collector endpoint. No Verify encrypts traffic but does not authenticate the NAS.

## Requests

| Purpose | Method and path |
| --- | --- |
| Login | POST `/cgi-bin/authLogin.cgi` |
| Health | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&sysHealth=1` |
| System | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&hd=no&multicpu=1` |
| CPU | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysmonitor&sys_cpu_use_v2=1&sys_memory_use=1` |
| Disk | GET `/cgi-bin/disk/qsmart.cgi?func=all_hd_data` |
| Volume | GET `/cgi-bin/management/chartReq.cgi?chart_func=disk_usage&disk_select=all&include=all` |
| iSCSI | GET `/cgi-bin/disk/iscsi_portal_setting.cgi?func=get_all` |
| Logout | GET `/cgi-bin/authLogout.cgi?logout=1` |

Authenticated calls append the session variable. Never publish SID-bearing URLs or raw responses. HTTP 200 alone is not proof of successful authentication or session invalidation.

## Deployment

1. Export/back up the existing design before an upgrade.
2. Import the JSON or apply changes to the existing design when preserving identity/history.
3. Configure collector, hostname, HTTPS port, credentials, and TLS Verify.
4. Test login, health, and session release; run full Builder collection.
5. Compare objects, values, and relationships with QTS.
6. Install or upgrade through Builder and configure/retain the integration account.
7. Verify scheduled collection, recent timestamps, positive capacities, stable IDs, and expected counts.
8. Configure the separate dashboard/alert content as appropriate for your environment.

## Limitations and security

Pool/RAID endpoints tested on this firmware returned HTTP 404. RAID groups, pools, initiator objects, IOPS, throughput, latency, and custom events are not modeled. Multi-real-volume, alternate-model/firmware, and multi-physical-CPU behavior require end-user validation. Fan mappings cover the tested hardware.

Do not publish credentials, encoded passwords, tokens, private hostnames/addresses, raw responses, serials, IQNs, NAA values, CHAP data, or storage paths. See the repository [security guidance](../SECURITY.md).
