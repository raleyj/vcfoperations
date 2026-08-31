"""Tests for the generated request graph, NOT the VCF Builder runtime."""
import copy
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from build_candidate import build, OUTPUT
from mock_redfish import fixtures, Handler

def resolve(value, key):
    for segment in key:
        if not isinstance(value, dict): return None
        value = value.get(segment)
    return value

def evaluate(design, responses):
    """A deliberately limited fixture evaluator: missing links skip branches.

    That policy is a test assumption, NOT proven Builder behavior. Rejects
    pagination and non-root-relative links rather than claiming to handle them.
    """
    results, attributes = {}, {}
    for wrapped in design['requests']:
        req = wrapped['request']
        chain = req.get('chainingSettings')
        if chain:
            param = chain['params'][0]
            attr = param['attributeExpression']['expressionParts'][0]['originId']
            if attr not in attributes: raise ValueError('Unknown chained attribute')
            paths = [resolve(row, attributes[attr]) for row in results[(chain['parentRequestId'], chain['baseListId'])]]
            paths = [path for path in paths if path is not None]
        else: paths = [req['path']]
        documents = []
        for path in paths:
            if not isinstance(path, str) or not path.startswith('/redfish/v1/') or '?' in path or '#' in path or '..' in path:
                raise ValueError('Unsupported resource URI')
            doc = responses[path]  # fail loudly on missing endpoint
            if not isinstance(doc, dict): raise ValueError('Invalid response')
            if 'Members@odata.nextLink' in doc: raise ValueError('Pagination requires Builder implementation')
            documents.append(doc)
        for model in req['response']['result']['dataModelLists']:
            rows = documents if model['id'] == 'base' else [member for doc in documents for member in resolve(doc, model['key'])]
            results[(req['id'], model['id'])] = rows
            for attr in model['attributes']: attributes[attr['id']] = attr['key']
    objects = []
    for wrapper in design['objects']:
        obj = wrapper['object']
        ms = obj['metricSets'][0]
        for row in results[(ms['requestId'], ms['listId'])]:
            values = {}
            for metric in ms['metrics']:
                origin = metric['expression']['expressionParts'][0]['originId']
                value = resolve(row, attributes[origin])
                if metric['dataType'] == 'NUMBER' and value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
                    raise ValueError('Non-numeric reading')
                values[metric['label']] = value
            if not values['@odata.id']: raise ValueError('Missing identity')
            objects.append((obj['internalObjectInfo']['objectTypeLabel'], values))
    return objects

class CandidateTests(unittest.TestCase):
    def test_reproducible_export(self):
        self.assertEqual(build(), json.loads(OUTPUT.read_text()))
    def test_multi_chassis_identities_and_units(self):
        rows = evaluate(build(), fixtures())
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({(kind, r['@odata.id']) for kind, r in rows}), 18)
        sensors = [r for kind, r in rows if kind == 'Dell Modern Sensor']
        self.assertEqual({r['ReadingUnits'] for r in sensors}, {'Cel', 'RPM', 'W'})
        fans = [r for kind, r in rows if kind == 'Dell Modern Fan']
        self.assertEqual(fans[0]['SpeedPercent.Reading'], 37.5)
        environment = [r for kind, r in rows if kind == 'Dell Modern Environment']
        self.assertEqual(environment[1]['PowerWatts.Reading'], 0)
        self.assertIsNone(environment[1]['TemperatureCelsius.Reading'])
    def test_missing_optional_branch_assumption(self):
        data = fixtures()
        del data['/redfish/v1/Chassis/Synthetic-2']['ThermalSubsystem']
        self.assertEqual(len(evaluate(build(), data)), 17)
    def test_empty_collection(self):
        data = fixtures()
        data['/redfish/v1/Systems']['Members'] = []
        self.assertEqual(len(evaluate(build(), data)), 16)
    def test_reject_pagination(self):
        data = fixtures()
        data['/redfish/v1/Systems']['Members@odata.nextLink'] = '/redfish/v1/Systems?$skip=2'
        with self.assertRaisesRegex(ValueError, 'Pagination'): evaluate(build(), data)
    def test_reject_external_uri(self):
        data = fixtures()
        data['/redfish/v1/']['Systems']['@odata.id'] = 'https://example.com/redfish/v1/Systems'
        with self.assertRaisesRegex(ValueError, 'URI'): evaluate(build(), data)
    def test_missing_endpoint_fails(self):
        data = fixtures()
        del data['/redfish/v1/Systems']
        with self.assertRaises(KeyError): evaluate(build(), data)
    def test_invalid_numeric_fails(self):
        data = fixtures()
        data['/redfish/v1/Chassis/Synthetic-1/Sensors/Temp']['Reading'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'Non-numeric'): evaluate(build(), data)
    def test_get_only_http_mock(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f'http://127.0.0.1:{server.server_port}/redfish/v1/') as response:
                self.assertEqual(json.load(response)['Systems']['@odata.id'], '/redfish/v1/Systems')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

if __name__ == '__main__': unittest.main()
