# UniFi compatibility and validation

## Recorded platform

- VCF Operations: 9.1.0.0400.25541561
- UDM Pro with UniFi OS 5.1.29 (Early Access)
- UniFi Network 10.5.67 (Official)
- Official local integration API through the UniFi OS proxy

The UniFi versions above come from the lab owner's screenshot. They are not a universal compatibility statement.

## August 31, 2026 evidence

- Device Details and Ports: live HTTP 200 with port index, state, connector and speed fields.
- WAN Interfaces: live HTTP 200 with two ID/name records; offset/limit paging test passed.
- Two full Builder collections succeeded: 159 objects, 959 properties and 315 relationships; 219 and 214 metric values respectively.
- Port identifiers include site, device and port index plus Builder adapter-instance scope.
- In-place upgrade completed as management pack 1.0.0.2; the existing account remains present and shows Collecting. Two scheduled cycles and sustained collection remain unverified.
- Export passed offline privacy/reference checks; no raw lab responses are included.

## Remaining validation

- Confirm installation and runtime account health; record two scheduled cycles and a 24–72 hour soak.
- Compare raw uplink rates with a same-window controlled traffic sample before assigning bits/bytes units.
- Exercise pagination beyond one page, multiple sites, offline devices, empty responses, optional/null fields, and API failures without flooding child alerts.
- Validate trusted TLS and least-privilege credentials. The lab Source test used No Verify; public defaults remain Verify.
- Verify history continuity and rollback before removing old accounts.
- Validate optional PoE and additional Operations content separately; they are not mapped in the current tested revision.

Other Network/UniFi OS versions and hosting layouts need their own endpoint, field and runtime checks. Legacy-only controllers are not covered.
