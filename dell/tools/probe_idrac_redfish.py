#!/usr/bin/env python3
"""Read-only Dell iDRAC Redfish compatibility probe.

Discovers resource IDs and reports which VCF Operations Builder profile can be
used. Credentials are read from environment variables and are never printed.
"""
import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
import urllib.parse


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect refused; configure the final iDRAC HTTPS hostname')


def resource_url(base, path):
    url = urllib.parse.urljoin(base, path)
    original, target = urllib.parse.urlsplit(base), urllib.parse.urlsplit(url)
    if (target.scheme, target.netloc) != (original.scheme, original.netloc):
        raise RuntimeError('Cross-origin Redfish link refused')
    if not target.path.startswith('/redfish/v1/') or target.fragment:
        raise RuntimeError('Invalid Redfish resource link')
    return url


def get(base, path, auth, context):
    request = urllib.request.Request(resource_url(base, path), headers={
        'Accept': 'application/json', 'Authorization': auth})
    try:
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context), NoRedirect())
        with opener.open(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise RuntimeError(f'GET {path} returned HTTP {exc.code}') from exc


def links(document):
    return [member.get('@odata.id') for member in (document or {}).get('Members', [])
            if isinstance(member, dict) and member.get('@odata.id')]


def main():
    parser = argparse.ArgumentParser(description='Probe iDRAC Redfish resources using GET only')
    parser.add_argument('host', help='iDRAC hostname or address')
    parser.add_argument('--port', type=int, default=443)
    parser.add_argument('--no-verify', action='store_true', help='Lab only: disable certificate verification')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON')
    args = parser.parse_args()
    username = os.environ.get('IDRAC_USERNAME')
    password = os.environ.get('IDRAC_PASSWORD')
    if not username or password is None:
        parser.error('set IDRAC_USERNAME and IDRAC_PASSWORD in the environment')
    token = base64.b64encode(f'{username}:{password}'.encode()).decode()
    auth = f'Basic {token}'
    context = ssl._create_unverified_context() if args.no_verify else ssl.create_default_context()
    base = f'https://{args.host}:{args.port}/redfish/v1/'

    root = get(base, '', auth, context)
    systems = links(get(base, 'Systems', auth, context))
    chassis = links(get(base, 'Chassis', auth, context))
    if not systems or not chassis:
        raise RuntimeError('Redfish Systems or Chassis collection is empty')
    system = systems[0]
    chassis_uri = chassis[0]
    chassis_doc = get(base, chassis_uri, auth, context)
    modern_power = (chassis_doc or {}).get('PowerSubsystem', {}).get('@odata.id')
    modern_thermal = (chassis_doc or {}).get('ThermalSubsystem', {}).get('@odata.id')
    sensors = (chassis_doc or {}).get('Sensors', {}).get('@odata.id')
    legacy_power = chassis_uri + '/Power'
    legacy_thermal = chassis_uri + '/Thermal'
    legacy_ok = bool(get(base, legacy_power, auth, context) and get(base, legacy_thermal, auth, context))
    modern_ok = bool(modern_power and modern_thermal and
                     get(base, modern_power, auth, context) and get(base, modern_thermal, auth, context))
    profile = 'modern' if modern_ok else ('legacy' if legacy_ok else 'unsupported')
    result = {
        'profile': profile,
        'redfish_version': (root or {}).get('RedfishVersion'),
        'system_uri': system,
        'chassis_uri': chassis_uri,
        'legacy': {'supported': legacy_ok, 'power_uri': legacy_power, 'thermal_uri': legacy_thermal},
        'modern': {'supported': modern_ok, 'power_subsystem_uri': modern_power,
                   'thermal_subsystem_uri': modern_thermal, 'sensors_uri': sensors},
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Detected resource family: {profile} (not a Builder support certification)")
        if profile == 'modern':
            print('Modern collector mappings are not included in the current Builder design.')
        print(f"Redfish version: {result['redfish_version'] or 'not reported'}")
        print(f"System: {system}")
        print(f"Chassis: {chassis_uri}")
        print(f"Legacy Power/Thermal: {'yes' if legacy_ok else 'no'}")
        print(f"Modern subsystems: {'yes' if modern_ok else 'no'}")
    return 0 if profile != 'unsupported' else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f'Probe failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
