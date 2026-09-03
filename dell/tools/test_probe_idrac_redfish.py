import unittest
from probe_idrac_redfish import resource_url, NoRedirect


class ResourceURLTests(unittest.TestCase):
    def test_relative_and_root_relative_links(self):
        base = 'https://idrac.example.com:443/redfish/v1/'
        for path in ('Systems', '/redfish/v1/Systems'):
            self.assertEqual(resource_url(base, path), base + 'Systems')
        self.assertEqual(resource_url(base, ''), base)

    def test_reject_untrusted_links(self):
        base = 'https://idrac.example.com/redfish/v1/'
        for path in ('https://other.example.com/redfish/v1/', '//other.example.com/',
                     'http://idrac.example.com/redfish/v1/', '/login', 'Systems#member'):
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                resource_url(base, path)

    def test_redirect_cannot_forward_credentials(self):
        with self.assertRaises(RuntimeError):
            NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example.com/')


if __name__ == '__main__':
    unittest.main()
