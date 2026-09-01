# QNAP Direct HTTPS

A community Management Pack Builder integration for monitoring QNAP QTS
directly from VMware Cloud Foundation Operations over HTTPS. No bridge appliance
is required.

## Download

- [Current Builder design JSON](designs/QNAP%20Direct%20HTTPS.json)
- [Release downloads](https://github.com/raleyj/vcfoperations/releases)

The JSON is a Management Pack Builder design, not a conventional `.pak`. Import
and install or upgrade it through **Build > Developer Center > Management Pack
Builder**.

## Tested release

| Component | Tested value |
| --- | --- |
| QNAP | TS-435XeU |
| QTS | 5.2.9.3451 |
| VCF Operations | 9.1.0.0400.25541561 |
| Installed integration | 1.0.0.7 |

The current design was upgraded in place. The existing account and installed
Volume Usage identity were retained. The account reported **Collecting** after
the upgrade. This is a community integration, not a QNAP or Broadcom certified
management pack.

## Coverage

| Object type | Coverage |
| --- | --- |
| QNAP Direct Array | Identity, firmware, memory, temperatures, fans, and numeric CPU usage |
| QNAP Direct Disk | Identity, health/status, capacity, temperature, and available SMART properties |
| QNAP Direct Volume Usage | Existing Volume ID binding with total and free capacity in bytes |
| QNAP Direct iSCSI Service | Service configuration and aggregate target, LUN, and initiator counts |
| QNAP Direct iSCSI Target | Stable identity, status, and mapped-LUN count |
| QNAP Direct iSCSI LUN | Stable identity, status, mapping, thin state, sector size, and capacity bytes |

The final live Builder verification completed in two seconds with 15 objects,
37 metrics, 84 properties, and 17 relationships. The tested NAS exposed one
array, six disks, one real volume, one iSCSI service, two targets, and two LUNs.
An inspected target status metric had two scheduled samples and an inspected
LUN capacity metric had one positive scheduled sample after the upgrade.

## QTS requests

| Purpose | Method and path |
| --- | --- |
| Login | POST `/cgi-bin/authLogin.cgi` |
| Health | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&sysHealth=1` |
| System statistics | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysinfo&hd=no&multicpu=1` |
| CPU statistics | GET `/cgi-bin/management/manaRequest.cgi?subfunc=sysmonitor&sys_cpu_use_v2=1&sys_memory_use=1` |
| Disk health | GET `/cgi-bin/disk/qsmart.cgi?func=all_hd_data` |
| Volume usage | GET `/cgi-bin/management/chartReq.cgi?chart_func=disk_usage&disk_select=all&include=all` |
| iSCSI inventory | GET `/cgi-bin/disk/iscsi_portal_setting.cgi?func=get_all` |
| Logout | GET `/cgi-bin/authLogout.cgi?logout=1` |

Authenticated requests append the Builder session variable. Treat request URLs
and diagnostic logs as sensitive.

## Account and credentials

The tested system, disk, and volume requests used the QTS **System Monitoring**
permission. iSCSI inventory required **System Management** on the tested NAS.
System Management is a broad role; shared-folder read-only access does not make
it a read-only system role.

The login request uses form encoding:

1. URL-encode the QTS username. An alphanumeric username is unchanged.
2. Base64-encode the password's UTF-8 bytes.
3. URL-encode the Base64 result, including `+`, `/`, and `=`.
4. Enter it in **Encoded Password**.

The encoded password remains a password-equivalent secret. Generate it locally,
never with an online encoder.

## Import or upgrade

1. Back up/export the existing Builder design when upgrading.
2. Import the current JSON into Management Pack Builder, or apply the changes to
   the existing design when history and identities must be preserved.
3. Configure a collector, NAS hostname, HTTPS port, Username, Encoded Password,
   and TLS mode. Keep **Verify** enabled with a trusted certificate whose SAN
   matches the configured hostname.
4. Test session creation, health, and session release. HTTP 200 alone does not
   prove QTS authentication succeeded.
5. Run **Verify > Perform Collection** and inspect the returned inventory.
6. Install or upgrade through Builder.
7. Configure or retain the installed integration account separately from the
   Builder test credentials.
8. Confirm Collecting status, recent timestamps, expected object counts, and
   plausible values against QTS.

## Remaining validation boundaries

- Complete a real 24-72 hour soak and controlled authentication, partial-request,
  credential-rotation, and TLS failure/recovery tests.
- Validate more than one real data volume, additional QTS versions, and
  multi-physical-CPU models.
- Prove a narrower monitoring-only permission profile or separate no-iSCSI
  edition if denied iSCSI access cannot be isolated.
- Discover stable pool/RAID endpoints before adding pool or RAID objects.
- Build and test dashboards and alert definitions after sufficient scheduled
  target/LUN history exists.
- RAID groups, pools, IOPS, throughput, latency, initiator objects, dashboards,
  alerts, and custom events are not included in this Builder design.

## Security

Do not publish credentials, encoded passwords, session IDs, response bodies,
private addresses, hostnames, IQNs, NAA values, CHAP data, storage paths, or
device serials in issues or screenshots. See [SECURITY.md](../SECURITY.md).
