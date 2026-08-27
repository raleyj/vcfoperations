"""Limited, offline publication checks; does not replace Builder validation."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def leaves(value, path='$'):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, f'{path}.{key}')
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from leaves(item, f'{path}[{index}]')
    else:
        yield path, value


def validate(path):
    raw = path.read_bytes()
    design = json.loads(raw)
    errors = []
    config = {item['key']: item for item in design['source']['configuration']}
    if config['mpb_hostname']['defaultValue'] != '':
        errors.append('Hostname default is not empty')
    if config['mpb_ssl_config']['defaultValue'] != 'Verify':
        errors.append('TLS verification is not the default')
    auth = design['source']['source']['authentication']
    for credential in auth['creds']:
        if any(key in credential for key in ('value', 'defaultValue', 'password', 'token')):
            errors.append('Credential contains a stored-value field')
        if not re.fullmatch(r'\$\{authentication\.credentials\.[a-z_]+\}', credential['usage']):
            errors.append('Credential usage is not a reference')
        if credential['label'] != 'Username' and credential.get('sensitive') is not True:
            errors.append('Secret credential is not marked sensitive')
    scalar_values = list(leaves(design))
    patterns = {
        'IPv4-like literal': r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])',
        'MAC-like literal': r'(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',
        'internal hostname': r'(?i)\.(?:local|internal|lan)\b',
        'private key': r'-----BEGIN .*PRIVATE KEY',
        'literal authorization': r'(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]+',
        'absolute host URL': r'https?://',
        'Windows path': r'[A-Za-z]:\\',
    }
    for location, value in scalar_values:
        if isinstance(value, str):
            for label, pattern in patterns.items():
                if re.search(pattern, value):
                    errors.append(f'{label} at {location} (value omitted)')
    ids = {value for location, value in scalar_values if location.endswith('.id') and isinstance(value, str)}
    reference_fields = ('.originId', '.requestId', '.parentRequestId', '.parentObjectId', '.childObjectId')
    for location, value in scalar_values:
        if location.endswith(reference_fields) and value and value not in ids:
            errors.append(f'Unresolved structural reference at {location}')
    print(f'{path.relative_to(ROOT)}: {len(design["objects"])} object types, '
          f'{len(design["requests"])} requests, {len(scalar_values)} scalar values')
    print(f'SHA256 {hashlib.sha256(raw).hexdigest()}')
    for error in errors:
        print(f'ERROR: {error}')
    return errors


def main():
    files = sorted(ROOT.glob('*/designs/*.json'))
    if len(files) != 2:
        print(f'Expected two designs; found {len(files)}')
        return 1
    errors = []
    for path in files:
        errors.extend(validate(path))
    print('Static checks passed.' if not errors else 'Static checks failed.')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
