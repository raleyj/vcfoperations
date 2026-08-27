# Security

Design exports must be reviewed before each publication. An earlier clean export does not guarantee a later export is safe.

Never publish actual credentials, API keys, encoded passwords, session cookies/IDs, private hosts, device serial numbers, MAC addresses, or captured inventory. Credential definitions and structural Builder UUIDs are necessary parts of a reusable design; do not remove them merely because they contain words such as password or ID.

Keep host defaults blank and TLS verification enabled. Enter environment values through Builder and integration-account settings. Base64 encoding does not protect a secret.

Do not post secrets or exploit details in a public issue. If a secret was exposed, revoke or rotate it promptly; deleting the current file does not remove it from Git history or downloaded copies.

The included validation script provides limited static checks. It does not replace manual review, vendor schema validation, or runtime testing.
