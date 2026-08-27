# Design validation and release packaging

Run these commands from the repository root with Python 3. No third-party Python packages are required.

## Validate designs and guides

```sh
python tools/validate_designs.py
```

Checks all three Builder designs for blank host defaults, TLS verification, credential references, selected sensitive-value patterns, and structural references. Also checks matching guide sections and local guide links. These static checks do not replace manual privacy review or testing in VCF Operations.

## Build distribution ZIPs

```sh
python tools/package_designs.py
```

Runs validation and builds one versioned ZIP per integration under the Git-ignored `dist/` folder. Each ZIP contains its design JSON, current README, license, and security guidance. `dist/SHA256SUMS.txt` records the ZIP checksums.

These archives contain Builder designs, not installable `.pak` files. Building an archive does not publish a GitHub release. Review the contents before uploading, and do not silently replace an existing release asset with a changed archive using the same filename.
