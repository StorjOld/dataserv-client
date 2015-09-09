import unittest
from dataserv_client import deserialize
from dataserv_client import exceptions


class TestUrl(unittest.TestCase):

    def test_url(self):

        # test http
        urlstr = "http://test.url.com"
        self.assertEqual(deserialize.url(urlstr), urlstr)

        # test https
        urlstr = "https://test.url.com"
        self.assertEqual(deserialize.url(urlstr), urlstr)

        # test ip
        urlstr = "https://127.0.0.1"
        self.assertEqual(deserialize.url(urlstr), urlstr)

        # test port
        urlstr = "https://127.0.0.1:5000"
        self.assertEqual(deserialize.url(urlstr), urlstr)

        # test ignores case
        urlstr = "HTTP://TEST.URL.COM"
        self.assertEqual(deserialize.url(urlstr), urlstr)

        # test invalid
        def callback():
            deserialize.url("--?%>=_`~$")
        self.assertRaises(exceptions.InvalidUrl, callback)


class TestByteCount(unittest.TestCase):

    def test_types(self):

        # accepted types
        self.assertEqual(deserialize.byte_count(1), 1)
        self.assertEqual(deserialize.byte_count("1"), 1)
        self.assertEqual(deserialize.byte_count(b"1"), 1)
        self.assertEqual(deserialize.byte_count(u"1"), 1)

        def callback():
            deserialize.byte_count(None)
        self.assertRaises(exceptions.InvalidInput, callback)

        def callback():
            deserialize.byte_count(1.0)
        self.assertRaises(exceptions.InvalidInput, callback)

    def test_int(self):
        self.assertEqual(deserialize.byte_count(1), 1)

    def test_no_postfix(self):
        self.assertEqual(deserialize.byte_count("1"), 1)
        self.assertEqual(deserialize.byte_count("2"), 2)

    def test_base_1024(self):
        self.assertEqual(deserialize.byte_count("1K"), 1 * (1024 ** 1))
        self.assertEqual(deserialize.byte_count("2K"), 2 * (1024 ** 1))

        self.assertEqual(deserialize.byte_count("1M"), 1 * (1024 ** 2))
        self.assertEqual(deserialize.byte_count("2M"), 2 * (1024 ** 2))

        self.assertEqual(deserialize.byte_count("1G"), 1 * (1024 ** 3))
        self.assertEqual(deserialize.byte_count("2G"), 2 * (1024 ** 3))

        self.assertEqual(deserialize.byte_count("1T"), 1 * (1024 ** 4))
        self.assertEqual(deserialize.byte_count("2T"), 2 * (1024 ** 4))

        self.assertEqual(deserialize.byte_count("1P"), 1 * (1024 ** 5))
        self.assertEqual(deserialize.byte_count("2P"), 2 * (1024 ** 5))

    def test_base_1000(self):
        self.assertEqual(deserialize.byte_count("1KB"), 1 * (1000 ** 1))
        self.assertEqual(deserialize.byte_count("2KB"), 2 * (1000 ** 1))

        self.assertEqual(deserialize.byte_count("1MB"), 1 * (1000 ** 2))
        self.assertEqual(deserialize.byte_count("2MB"), 2 * (1000 ** 2))

        self.assertEqual(deserialize.byte_count("1GB"), 1 * (1000 ** 3))
        self.assertEqual(deserialize.byte_count("2GB"), 2 * (1000 ** 3))

        self.assertEqual(deserialize.byte_count("1TB"), 1 * (1000 ** 4))
        self.assertEqual(deserialize.byte_count("2TB"), 2 * (1000 ** 4))

        self.assertEqual(deserialize.byte_count("1PB"), 1 * (1000 ** 5))
        self.assertEqual(deserialize.byte_count("2PB"), 2 * (1000 ** 5))

    def test_decimal(self):
        # test unit boundries base 1024
        self.assertEqual(deserialize.byte_count("1.0K"), 1024 ** 1)
        self.assertEqual(deserialize.byte_count("1.0M"), 1024 ** 2)
        self.assertEqual(deserialize.byte_count("1.0G"), 1024 ** 3)
        self.assertEqual(deserialize.byte_count("1.0T"), 1024 ** 4)
        self.assertEqual(deserialize.byte_count("1.0P"), 1024 ** 5)

        # test unit boundries base 1000
        self.assertEqual(deserialize.byte_count("1.0KB"), 1000 ** 1)
        self.assertEqual(deserialize.byte_count("1.0MB"), 1000 ** 2)
        self.assertEqual(deserialize.byte_count("1.0GB"), 1000 ** 3)
        self.assertEqual(deserialize.byte_count("1.0TB"), 1000 ** 4)
        self.assertEqual(deserialize.byte_count("1.0PB"), 1000 ** 5)

        # test between unit boundries base 1024
        self.assertEqual(deserialize.byte_count("0.5K"), (1024 ** 1 / 2))
        self.assertEqual(deserialize.byte_count("0.5M"), (1024 ** 2 / 2))
        self.assertEqual(deserialize.byte_count("0.5G"), (1024 ** 3 / 2))
        self.assertEqual(deserialize.byte_count("0.5T"), (1024 ** 4 / 2))
        self.assertEqual(deserialize.byte_count("0.5P"), (1024 ** 5 / 2))

        # test between unit boundries base 1000
        self.assertEqual(deserialize.byte_count("0.5KB"), (1000 ** 1 / 2))
        self.assertEqual(deserialize.byte_count("0.5MB"), (1000 ** 2 / 2))
        self.assertEqual(deserialize.byte_count("0.5GB"), (1000 ** 3 / 2))
        self.assertEqual(deserialize.byte_count("0.5TB"), (1000 ** 4 / 2))
        self.assertEqual(deserialize.byte_count("0.5PB"), (1000 ** 5 / 2))

        # test type
        self.assertTrue(isinstance(deserialize.byte_count("0.49K"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49M"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49G"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49T"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49P"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49KB"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49MB"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49GB"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49TB"), int))
        self.assertTrue(isinstance(deserialize.byte_count("0.49PB"), int))


if __name__ == '__main__':
    unittest.main()
