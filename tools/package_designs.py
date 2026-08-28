"""Build local draft release archives from an explicit file allowlist."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / 'tools/validate_designs.py')], check=True)
output = ROOT / 'dist'
output.mkdir(exist_ok=True)
checksums = []
for folder, prefix in [('qnap', 'qnap-direct-https'),
                       ('ubiquiti', 'ubiquiti-unifi-network'),
                       ('dell', 'dell-idrac-redfish'),
                       ('hpe', 'hpe-ilo-redfish')]:
    designs = sorted((ROOT / folder / 'designs').glob('*.json'))
    version = json.loads(designs[0].read_bytes())['design']['design']['version']
    if not version or any(c not in '0123456789.-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in version):
        raise ValueError('Unsafe version string')
    name = f'{prefix}-{version}-design.zip'
    target = output / name
    files = [ROOT / folder / 'README.md', ROOT / 'LICENSE', ROOT / 'SECURITY.md']
    files += designs
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name if path.parent == ROOT else path.relative_to(ROOT / folder).as_posix())
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f'Archive validation failed: {target}')
    checksums.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {name}')
    print(f'Built and verified {target.name}')
(output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
