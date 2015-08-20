import unittest
from dataserv_client import deserialize


class TestByteCount(unittest.TestCase):

    # FIXME test failure modes

    def test_int(self):
        self.assertEqual(deserialize.byte_count(0), 0)
        self.assertEqual(deserialize.byte_count(1), 1)

    def test_no_postfix(self):
        self.assertEqual(deserialize.byte_count("0"), 0)
        self.assertEqual(deserialize.byte_count("1"), 1)
        self.assertEqual(deserialize.byte_count("2"), 2)

    def test_base_1024(self):
        self.assertEqual(deserialize.byte_count("0K"), 0 * (1024 ** 1))
        self.assertEqual(deserialize.byte_count("1K"), 1 * (1024 ** 1))
        self.assertEqual(deserialize.byte_count("2K"), 2 * (1024 ** 1))

        self.assertEqual(deserialize.byte_count("0M"), 0 * (1024 ** 2))
        self.assertEqual(deserialize.byte_count("1M"), 1 * (1024 ** 2))
        self.assertEqual(deserialize.byte_count("2M"), 2 * (1024 ** 2))

        self.assertEqual(deserialize.byte_count("0G"), 0 * (1024 ** 3))
        self.assertEqual(deserialize.byte_count("1G"), 1 * (1024 ** 3))
        self.assertEqual(deserialize.byte_count("2G"), 2 * (1024 ** 3))

        self.assertEqual(deserialize.byte_count("0T"), 0 * (1024 ** 4))
        self.assertEqual(deserialize.byte_count("1T"), 1 * (1024 ** 4))
        self.assertEqual(deserialize.byte_count("2T"), 2 * (1024 ** 4))

        self.assertEqual(deserialize.byte_count("0P"), 0 * (1024 ** 5))
        self.assertEqual(deserialize.byte_count("1P"), 1 * (1024 ** 5))
        self.assertEqual(deserialize.byte_count("2P"), 2 * (1024 ** 5))

    def test_base_1000(self):
        self.assertEqual(deserialize.byte_count("0KB"), 0 * (1000 ** 1))
        self.assertEqual(deserialize.byte_count("1KB"), 1 * (1000 ** 1))
        self.assertEqual(deserialize.byte_count("2KB"), 2 * (1000 ** 1))

        self.assertEqual(deserialize.byte_count("0MB"), 0 * (1000 ** 2))
        self.assertEqual(deserialize.byte_count("1MB"), 1 * (1000 ** 2))
        self.assertEqual(deserialize.byte_count("2MB"), 2 * (1000 ** 2))

        self.assertEqual(deserialize.byte_count("0GB"), 0 * (1000 ** 3))
        self.assertEqual(deserialize.byte_count("1GB"), 1 * (1000 ** 3))
        self.assertEqual(deserialize.byte_count("2GB"), 2 * (1000 ** 3))

        self.assertEqual(deserialize.byte_count("0TB"), 0 * (1000 ** 4))
        self.assertEqual(deserialize.byte_count("1TB"), 1 * (1000 ** 4))
        self.assertEqual(deserialize.byte_count("2TB"), 2 * (1000 ** 4))

        self.assertEqual(deserialize.byte_count("0PB"), 0 * (1000 ** 5))
        self.assertEqual(deserialize.byte_count("1PB"), 1 * (1000 ** 5))
        self.assertEqual(deserialize.byte_count("2PB"), 2 * (1000 ** 5))


if __name__ == '__main__':
    unittest.main()
