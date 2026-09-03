# QNAP Direct HTTPS bundle 1.1.1

This distribution refresh packages the existing six-object Builder export used by the integration reported as 1.0.0.7. No collector logic or object identifiers were changed; only the stale design description was refreshed. The internal design version remains 1.0.0.

- Documents the completed minimum 24-hour scheduled observation with stable two-target/two-LUN inventory.
- Documents the separately configured QNAP dashboard, disk-temperature warning, and LUN-state critical alert.
- Records independent QTS session, request-failure, invalid-credential, and TLS-client rejection checks, with explicit limits on what those tests prove.
- Retains the tested TS-435XeU/QTS 5.2.9.3451/VCF Operations 9.1.0.0400.25541561 boundary.

The archive is **not a `.pak`** and does not include exported dashboards, alert definitions, policies, or super metrics. See [README.md](README.md) for deployment and the precise validation scope.
