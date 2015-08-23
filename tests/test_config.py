import os
import unittest
import tempfile
from dataserv_client import config
from dataserv_client import version


class TestConfig(unittest.TestCase):

    def test_roundtrip_unencrypted(self):
        path = tempfile.mktemp()
        input_data = {
            "version": version.__version__,
            "wallet": {
                "master_secret": "",
            },
            "payout_address": "1A8WqiJDh3tGVeEefbMN5BVDYxx2XSoWgG",
            "cold_storage": {
                "pub_hwifs": [],
                "addresses": [],
            },
            "storage_dirs": [
                {"path": "~/.storj/store", "capacity": 1024 * 1024 * 1024},
            ]
        }
        config.save(path, input_data)
        output_data = config.load(path)
        self.assertEqual(input_data, output_data)
        os.remove(path)

    def test_validation(self):
        pass  # TODO test valid password types "", b"", u""


if __name__ == '__main__':
    unittest.main()
