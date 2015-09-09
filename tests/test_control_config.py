import os
import copy
import unittest
import tempfile

from btctxstore import BtcTxStore
from dataserv_client.control import config
from dataserv_client import __version__
from dataserv_client import exceptions


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

    def test_validation(self):
        wallet = self.btctxstore.create_wallet()
        key = self.btctxstore.get_key(wallet)
        address = self.btctxstore.get_address(key)

        # must be a dict
        def callback():
            config.validate(self.btctxstore, None)
        self.assertRaises(exceptions.InvalidConfig, callback)

        # must have the correct version
        def callback():
            config.validate(self.btctxstore, {
                "payout_address": address,
                "wallet": wallet,
            })
        self.assertRaises(exceptions.InvalidConfig, callback)

        # must have a valid payout address
        def callback():
            config.validate(self.btctxstore, {
                "version": __version__,
                "wallet": wallet,
            })
        self.assertRaises(exceptions.InvalidConfig, callback)

        # must have a valid wallet
        def callback():
            config.validate(self.btctxstore, {
                "version": __version__,
                "payout_address": address,
            })
        self.assertRaises(exceptions.InvalidConfig, callback)

        # valid config
        self.assertTrue(config.validate(self.btctxstore, {
            "version": __version__,
            "payout_address": address,
            "wallet": wallet,
        }))

    def test_migrate(self):
        path = tempfile.mktemp()

        # initial unmigrated 2.0.0 config
        cfg = {
            "version": "2.0.0",
            "master_secret": "test_master_secret",
            "payout_address": "1A8WqiJDh3tGVeEefbMN5BVDYxx2XSoWgG",
        }

        # test its invalid with current build
        def callback():
            config.validate(self.btctxstore, cfg)
        self.assertRaises(exceptions.InvalidConfig, callback)

        # migrate
        cfg = config.migrate(self.btctxstore, path, cfg)

        # test its now valid
        self.assertTrue(config.validate(self.btctxstore, cfg))


if __name__ == '__main__':
    unittest.main()
