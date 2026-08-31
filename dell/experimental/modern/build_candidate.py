"""Generate an EXPERIMENTAL Builder design from standard Redfish resource shapes."""
import copy
import json
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'Dell iDRAC Modern Redfish Candidate.json'

def uid(key):
    return str(uuid5(NAMESPACE_URL, 'vcf-dell-modern-candidate/' + key))

def expression(origin, kind='ATTRIBUTE'):
    part = uid('part/' + origin)
    return {'id': uid('expression/' + origin), 'expressionText': f'@@@MPB_QUOTE {part} @@@MPB_QUOTE',
            'expressionParts': [{'id': part, 'originType': kind, 'originId': origin}]}

def build():
    legacy = json.loads((HERE.parents[1] / 'designs' / 'Dell iDRAC Redfish.json').read_text())
    source = copy.deepcopy(legacy['source'])
    def reidentify(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == 'id': value[k] = uid('source/' + v)
                else: reidentify(v)
        elif isinstance(value, list):
            for item in value: reidentify(item)
    reidentify(source)
    source['source']['configuration']['baseApiPath'] = ''
    source['source']['testRequest']['path'] = '/redfish/v1/'
    design = {'type': 'HTTP', 'design': {'design': {
        'name': 'Dell iDRAC Modern Redfish Candidate', 'type': 'HTTP', 'version': '0.1.0',
        'opsVersion': legacy['design']['design']['opsVersion'],
        'description': 'EXPERIMENTAL. Standard modern Redfish candidate for iDRAC9/iDRAC10 evaluation. Synthetic fixtures only; no real modern iDRAC validation. Not a supported replacement for the legacy Dell pack. Uses linked PowerSubsystem, ThermalSubsystem, EnvironmentMetrics and Sensors. Optional branches, pagination, Builder URL handling and runtime collection require validation.'}},
        'source': source, 'objects': [], 'relationships': [], 'events': [], 'requests': []}
    requests = {}
    def request(name, fields, parent=None, link=None, collection=False, path=None):
        rid = uid('request/' + name)
        fields = list(dict.fromkeys(fields))
        lists = [{'id': 'base', 'key': [], 'attributes': []}]
        if collection:
            lists.append({'id': 'Members.*', 'label': 'Members.*', 'key': ['Members'],
                          'parentListId': 'base', 'attributes': []})
        target = lists[-1]
        for field in fields:
            key = field.split('.') if '@odata.id' not in field else field[:-9].rstrip('.').split('.') + ['@odata.id'] if field != '@odata.id' else ['@odata.id']
            target['attributes'].append({'id': f'{rid}-{target["id"]}-{field}', 'label': field, 'key': key})
        req = {'id': rid, 'name': name, 'path': path or '${requestParameters.resource}',
               'method': 'GET', 'body': '', 'headers': [], 'params': [],
               'response': {'result': {'responseCode': 200, 'dataModelLists': lists}}}
        if parent:
            pr = requests[parent]
            lid = pr['response']['result']['dataModelLists'][-1]['id']
            req['chainingSettings'] = {'id': uid('chain/' + name), 'parentRequestId': pr['id'],
                'baseListId': lid, 'params': [{'id': uid('param/' + name), 'label': 'Resource URI',
                    'listId': lid, 'attributeExpression': expression(f'{pr["id"]}-{lid}-{link}'),
                    'key': 'resource', 'usage': '${requestParameters.resource}'}]}
        requests[name] = req
        design['requests'].append({'request': req})
        return req
    common = ['@odata.id', 'Id', 'Name', 'Status.Health', 'Status.State']
    request('Service root', ['Systems.@odata.id', 'Chassis.@odata.id'], path='/redfish/v1/')
    request('Systems', ['@odata.id'], 'Service root', 'Systems.@odata.id', True)
    request('Server', common + ['Manufacturer', 'Model', 'SerialNumber', 'PowerState', 'BiosVersion'], 'Systems', '@odata.id')
    request('Chassis collection', ['@odata.id'], 'Service root', 'Chassis.@odata.id', True)
    request('Chassis', common + ['EnvironmentMetrics.@odata.id', 'PowerSubsystem.@odata.id', 'ThermalSubsystem.@odata.id', 'Sensors.@odata.id'], 'Chassis collection', '@odata.id')
    request('Environment', ['@odata.id', 'Name', 'PowerWatts.Reading', 'TemperatureCelsius.Reading'], 'Chassis', 'EnvironmentMetrics.@odata.id')
    request('Power subsystem', ['PowerSupplies.@odata.id'], 'Chassis', 'PowerSubsystem.@odata.id')
    request('Power supplies', ['@odata.id'], 'Power subsystem', 'PowerSupplies.@odata.id', True)
    request('Power supply', common + ['Model', 'SerialNumber', 'Metrics.@odata.id'], 'Power supplies', '@odata.id')
    request('Power supply metrics', ['@odata.id', 'Name', 'InputPowerWatts.Reading', 'OutputPowerWatts.Reading', 'InputVoltage.Reading'], 'Power supply', 'Metrics.@odata.id')
    request('Thermal subsystem', ['Fans.@odata.id'], 'Chassis', 'ThermalSubsystem.@odata.id')
    request('Fans', ['@odata.id'], 'Thermal subsystem', 'Fans.@odata.id', True)
    request('Fan', common + ['SpeedPercent.Reading'], 'Fans', '@odata.id')
    request('Sensors', ['@odata.id'], 'Chassis', 'Sensors.@odata.id', True)
    request('Sensor', common + ['Reading', 'ReadingType', 'ReadingUnits'], 'Sensors', '@odata.id')
    for name in ['Server', 'Chassis', 'Environment', 'Power supply', 'Power supply metrics', 'Fan', 'Sensor']:
        req = requests[name]
        metrics = []
        for attr in req['response']['result']['dataModelLists'][0]['attributes']:
            field = attr['label']
            if field != '@odata.id' and field.endswith('@odata.id'): continue
            number = field == 'Reading' or field.endswith('.Reading')
            metrics.append({'id': uid('metric/' + name + '/' + field), 'label': field,
                'dataType': 'NUMBER' if number else 'STRING', 'expression': expression(attr['id']),
                'isKpi': False, 'usage': 'METRIC' if number else 'PROPERTY', 'unit': '', 'groups': []})
        identity = metrics[0]['id']
        design['objects'].append({'object': {'designType': 'HTTP', 'id': uid('object/' + name),
            'type': 'INTERNAL', 'isListObject': False,
            'metricSets': [{'id': uid('metricset/' + name), 'metrics': metrics, 'listId': 'base', 'requestId': req['id']}],
            'internalObjectInfo': {'objectTypeLabel': 'Dell Modern ' + name, 'icon': 'default.svg',
                'nameMetricExpression': expression(identity, 'METRIC'), 'identifierIds': [identity]}}})
    return design

if __name__ == '__main__':
    OUTPUT.write_text(json.dumps(build(), indent=2) + '\n', encoding='utf-8')
    print(OUTPUT)
