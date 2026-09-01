# QNAP Direct HTTPS 1.1.0

This repository release packages the current exported Management Pack Builder
design. The tested installed integration reports version 1.0.0.7 in VCF
Operations.

## Added

- Repeatable QNAP Direct iSCSI Target objects.
- Repeatable QNAP Direct iSCSI LUN objects.
- Target-to-LUN relationships using the mapped target index.
- LUN status, mapped state, thin-provisioning state, sector size, and exact
  capacity in bytes.
- Native numeric CPU Usage Percent while retaining the raw CPU property.

## Changed

- Rebound the existing Volume Usage type to the repeated volume response using
  the existing Volume ID property, preserving installed identity and history.
- Corrected memory and capacity units.
- Corrected QTS logout with `logout=1`.

## Validation

- TS-435XeU running QTS 5.2.9.3451.
- VCF Operations 9.1.0.0400.25541561.
- Live Builder verification: 15 objects, 37 metrics, 84 properties, and
  17 relationships in two seconds.
- Inventory: two targets and two LUNs.
- Existing account retained and Collecting after the in-place upgrade.

See [README.md](README.md) for setup, security guidance, and remaining
validation boundaries.
