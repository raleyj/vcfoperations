import unittest

from evaluate_legacy import normalize


class LegacySemanticsTests(unittest.TestCase):
    def test_powered_off_nulls_remain_unknown(self):
        result = normalize(
            {"UUID": "server-1", "PowerState": "Off", "Status": {"Health": "OK"}},
            {"PowerControl": [{"PowerConsumedWatts": None}]},
            {"Temperatures": [{"MemberId": "CPU1", "ReadingCelsius": None, "Status": {}}]},
        )
        self.assertIsNone(result["power"]["watts"])
        self.assertIsNone(result["temperatures"][0]["reading_c"])
        self.assertIsNone(result["temperatures"][0]["health"])

    def test_zero_is_preserved_when_source_reports_zero(self):
        result = normalize({}, {"PowerControl": [{"PowerConsumedWatts": 0}]}, {})
        self.assertEqual(result["power"]["watts"], 0)

    def test_empty_optional_collections_do_not_remove_server(self):
        result = normalize({"UUID": "server-1"}, {}, {"Fans": [], "Temperatures": []})
        self.assertEqual(result["server"]["id"], "server-1")
        self.assertEqual(result["fans"], [])
        self.assertEqual(result["temperatures"], [])

    def test_missing_optional_collections_are_empty(self):
        result = normalize({"UUID": "server-1"}, {}, {})
        self.assertEqual(result["fans"], [])
        self.assertEqual(result["supplies"], [])

    def test_partial_thermal_response_keeps_power(self):
        result = normalize({"UUID": "server-1"}, {"PowerControl": [{"PowerConsumedWatts": 215}]}, {})
        self.assertEqual(result["power"]["watts"], 215)
        self.assertEqual(result["temperatures"], [])

    def test_fan_identity_survives_serial_replacement(self):
        before = normalize({}, {}, {"Fans": [{"MemberId": "0", "FanName": "Fan1A", "SerialNumber": "old"}]})
        after = normalize({}, {}, {"Fans": [{"MemberId": "0", "FanName": "Fan1A", "SerialNumber": "new"}]})
        self.assertEqual(before["fans"][0]["id"], after["fans"][0]["id"])
        self.assertNotEqual(before["fans"][0]["serial"], after["fans"][0]["serial"])

    def test_schema_additions_are_ignored(self):
        result = normalize({"UUID": "server-1", "NewField": {"Anything": True}}, {}, {"NewArray": [1, 2]})
        self.assertEqual(result["server"]["id"], "server-1")

    def test_missing_member_id_falls_back_to_name(self):
        result = normalize({}, {}, {"Fans": [{"FanName": "Fan1A", "Reading": 8160, "ReadingUnits": "RPM"}]})
        self.assertEqual(result["fans"][0]["id"], "fan:Fan1A")

    def test_health_is_preserved_raw(self):
        result = normalize({}, {}, {"Fans": [{"MemberId": "0", "Status": {"Health": "Warning"}}]})
        self.assertEqual(result["fans"][0]["health"], "Warning")


if __name__ == "__main__":
    unittest.main()
