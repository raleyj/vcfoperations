# HPE iLO validation status

September 4, 2026. Further implementation and testing are paused. The installed lab package is 1.0.0.7; its Builder export retains design version 1.0.0. This record separates observed results from remaining limitations. It does not declare the three roadmap areas complete.

## Scope and method

Physical reference: DL360 Gen9, iLO 4 firmware 2.82, VCF Operations 9.1.0.0400.25541561. Built for best-effort iLO 4-7 compatibility; no newer hardware was tested. Controlled faults changed response copies delivered to the existing native collector through a temporary relay. They did not damage hardware, alter the hardware log or establish actual physical failure detection.

After testing, the existing account was restored to direct HTTPS with Verify. Four consecutive scheduled cycles retained 92 hardware objects, 216 metrics and fresh fan readings. The relay was stopped and its one-use private keys removed. No SDK deployment occurred.

## Completed checks

| Check | Observed result |
| --- | --- |
| Existing Builder upgrade | Package 1.0.0.7 installed while retaining the account and existing resource identities |
| Inventory and topology | 92 hardware objects; server linked to all 91 component children |
| Thermal HTTP 503 and 404 | Partial collection fell to 98 metrics without inventory loss; recovery returned to 216 |
| Thermal timeout | Retries observed and collection extended to about 145 seconds; recovery restored 216 metrics |
| Changed untrusted TLS certificate | No HTTP traffic accepted through the changed certificate; native metric count fell to zero and recovered afterward |
| Fan fault and recovery | One correctly associated Critical fan alert, no duplicate server alert, then Inactive after three healthy collections |
| Absent power-supply guard | Absent/Critical response did not trigger the Enabled-only rule |
| Offline temperature | Offline/zero response did not trigger the health rule; normal state and reading recovered |
| Maintenance | Native maintenance suppression verified |
| Basic IML lifecycle | Synthetic event created once during unchanged delivery; explicit repaired case canceled after three cycles |
| SDK prototype | Seven local logic/serialization tests passed; no native deployment or migration test |

The alert/dashboard checks describe separately configured lab content, not objects bundled in the downloadable JSON. Source-property timestamps and stored health must not be treated as proof of per-cycle freshness.

## Remaining limitations

| Area | Remaining behavior or verification |
| --- | --- |
| P0 collection assurance | Explicit unknown/stale component health and reliable partial-failure indication; scheduled power-off/transition test; certificate hostname rejection |
| P1 operational content | Alert behavior when health disappears; native content export/import and rollback; any SDK migration must preserve the existing account, objects and history |
| P2 event lifecycle | Missing Repaired inclusion; persistent identity across gaps, restarts and log resets; event clearing across recovery/account changes; residual synthetic-event cleanup |

When Fan Health was omitted, the existing Critical property and alert remained. Data receiving and zero no-data counts did not reveal every partial collection failure. Unavailable data is not a confirmed healthy state.

In the IML test, two collections omitted a new event without Repaired metadata. Changing only Created during continuous delivery did not produce a distinct event generation. Basic explicit-repair clearing passed, but a subsequent labeled CONTROLLED TEST event remained uncanceled after four direct recovery cycles. Its cause is unproven. Native Actions were disabled, no manual cleanup succeeded, and a scoped read-only API lookup returned HTTP 401. Hardware logs were untouched.

The API authorization failure also prevented verification of generated native identity keys for SDK migration. The offline checkpoint test was a JSON round trip, not production storage durability. No SDK replacement, registry image or cloud proxy was deployed. The existing Builder pack continues to collect with the limitations above.

## Release boundaries

The published artifact is the reviewed Builder JSON plus documentation and its checksum. The native content export was blocked by Chrome; separate dashboard/alert import and rollback remain unverified. No full lab exports, credentials, response captures, private keys or device identities are published. The work is paused, and uncompleted items remain limitations rather than being relabeled as passed.
