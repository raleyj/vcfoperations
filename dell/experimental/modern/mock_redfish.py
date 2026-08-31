"""Synthetic Redfish fixture service, NOT a Dell emulator. No credentials required.

Run locally: python mock_redfish.py --port 8088
Only GET is implemented. Binds loopback only; do not send real credentials.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def fixtures():
    data = {}
    def resource(path, **values):
        data[path] = {'@odata.id': path, **values}
        return {'@odata.id': path}
    def collection(path, members):
        return resource(path, Members=members, **{'Members@odata.count': len(members)})
    systems, chassis = [], []
    for number in (1, 2):
        s = f'/redfish/v1/Systems/Synthetic-{number}'
        c = f'/redfish/v1/Chassis/Synthetic-{number}'
        health = {'Health': 'OK' if number == 1 else 'Warning', 'State': 'Enabled'}
        systems.append(resource(s, Id=f'Synthetic-{number}', Name=f'Synthetic server {number}',
            Manufacturer='SYNTHETIC TEST DATA', Model='Not real Dell hardware', SerialNumber=f'MOCK{number}',
            PowerState='On' if number == 1 else 'Off', BiosVersion='fixture', Status=health))
        env = resource(c + '/EnvironmentMetrics', Name='Environment',
            PowerWatts={'Reading': 420 if number == 1 else 0},
            TemperatureCelsius={'Reading': 23 if number == 1 else None})
        ps = c + '/PowerSubsystem'
        p = ps + '/PowerSupplies/PSU1'
        pm = resource(p + '/Metrics', Name='PSU metrics', InputPowerWatts={'Reading': 230},
            OutputPowerWatts={'Reading': 210}, InputVoltage={'Reading': 240})
        supplies = collection(ps + '/PowerSupplies', [resource(p, Id='PSU1', Name='PSU 1',
            Status=health, Model='Mock supply', SerialNumber=f'PSU{number}', Metrics=pm)])
        power = resource(ps, PowerSupplies=supplies)
        ts = c + '/ThermalSubsystem'
        fans = collection(ts + '/Fans', [resource(ts + '/Fans/Fan1', Id='Fan1', Name='Fan 1',
            Status=health, SpeedPercent={'Reading': 37.5})])
        thermal = resource(ts, Fans=fans)
        sensor_members = []
        for sid, reading, kind, unit in [('Temp', 24.5, 'Temperature', 'Cel'),
                                          ('Fan', 12000, 'Rotational', 'RPM'),
                                          ('Power', 0, 'Power', 'W')]:
            sensor_members.append(resource(c + '/Sensors/' + sid, Id=sid, Name=sid,
                Status=health, Reading=reading, ReadingType=kind, ReadingUnits=unit))
        sensors = collection(c + '/Sensors', sensor_members)
        chassis.append(resource(c, Id=f'Synthetic-{number}', Name=f'Chassis {number}', Status=health,
            EnvironmentMetrics=env, PowerSubsystem=power, ThermalSubsystem=thermal, Sensors=sensors))
    resource('/redfish/v1/', Systems=collection('/redfish/v1/Systems', systems),
             Chassis=collection('/redfish/v1/Chassis', chassis), RedfishVersion='1.16.0',
             Name='SYNTHETIC modern Redfish fixture - not Dell firmware')
    return data

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = fixtures().get(self.path)
        self.send_response(200 if payload is not None else 404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload if payload is not None else {'error': 'Fixture not found'}).encode())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8088)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Synthetic fixtures only: http://127.0.0.1:{server.server_port}/redfish/v1/', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
