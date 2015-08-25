import os
import copy
import unittest
import tempfile
from btctxstore import BtcTxStore
from dataserv_client import config
from dataserv_client import version


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.btctxstore = BtcTxStore()

    def test_roundtrip_unencrypted(self):
        path = tempfile.mktemp()
        saved_data = config.create(self.btctxstore, path)
        loaded_data = config.get(self.btctxstore, path)
        self.assertEqual(saved_data, loaded_data)
        os.remove(path)

    def test_save_overwrites(self):
        path = tempfile.mktemp()

        # create config
        created_data = config.create(self.btctxstore, path)

        # update config
        updated_data = copy.deepcopy(created_data)
        updated_data["payout_address"] = "1A8WqiJDh3tGVeEefbMN5BVDYxx2XSoWgG"
        config.save(self.btctxstore, path, updated_data)

        # confirm overwriten
        loaded_data = config.get(self.btctxstore, path)
        self.assertEqual(updated_data, loaded_data)
        os.remove(path)

    def test_password_validation(self):
        pass  # TODO implement

    def test_validate(self):
        pass  # TODO implement

    def test_create(self):
        pass  # TODO implement

    def test_get(self):
        pass  # TODO implement


if __name__ == '__main__':
    unittest.main()
