from dataserv_client import common

import time
import tempfile
import unittest
import datetime

from dataserv_client import cli
from dataserv_client import api
from btctxstore import BtcTxStore
from dataserv_client import exceptions


url = "http://127.0.0.1:5000"
common.SHARD_SIZE = 1024 * 128  # monkey patch shard size to 128K


class AbstractTestSetup(object):
    def setUp(self):
        self.btctxstore = BtcTxStore()
        time.sleep(2)  # avoid collision


class TestClientRegister(AbstractTestSetup, unittest.TestCase):
    def test_register(self):
        client = api.Client(url=url, config_path=tempfile.mktemp())
        self.assertTrue(client.register())

    def test_already_registered(self):
        def callback():
            client = api.Client(url=url, config_path=tempfile.mktemp())
            client.register()
            client.register()

        self.assertRaises(exceptions.AddressAlreadyRegistered, callback)

    def test_invalid_farmer(self):
        def callback():
            client = api.Client(url=url + "/xyz",
                                config_path=tempfile.mktemp())
            client.register()

        self.assertRaises(exceptions.ServerNotFound, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):
    def test_ping(self):
        client = api.Client(url=url, config_path=tempfile.mktemp())
        self.assertTrue(client.register())
        self.assertTrue(client.ping())

    def test_invalid_farmer(self):
        def callback():
            client = api.Client(url=url + "/xyz",
                                config_path=tempfile.mktemp())
            client.ping()

        self.assertRaises(exceptions.ServerNotFound, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):
    def test_poll(self):
        client = api.Client(url=url, config_path=tempfile.mktemp())
        client.register()
        self.assertTrue(client.poll(delay=2, limit=10))


class TestInvalidArgument(AbstractTestSetup, unittest.TestCase):
    def test_invalid_retry_limit(self):
        def callback():
            api.Client(connection_retry_limit=-1,
                       config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_retry_delay(self):
        def callback():
            api.Client(connection_retry_delay=-1,
                       config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_negativ_max_size(self):
        def callback():
            api.Client(max_size=-1, config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_zero_max_size(self):
        def callback():
            api.Client(max_size=0, config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_negative_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.build(set_height_interval=-1)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_zero_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.build(set_height_interval=0)

        self.assertRaises(exceptions.InvalidInput, callback)


class TestConnectionRetry(AbstractTestSetup, unittest.TestCase):
    def test_no_retry(self):
        def callback():
            client = api.Client(url="http://invalid.url",
                                connection_retry_limit=0,
                                connection_retry_delay=0,
                                config_path=tempfile.mktemp())
            client.register()

        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=15) > (after - before))

    def test_default_retry(self):
        def callback():
            client = api.Client(url="http://invalid.url",
                                config_path=tempfile.mktemp(),
                                connection_retry_limit=5,
                                connection_retry_delay=5)
            client.register()

        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=25) < (after - before))


class TestClientBuild(AbstractTestSetup, unittest.TestCase):
    def test_build(self):
        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            max_size=1024 * 256)  # 256K
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated))

        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            max_size=1024 * 512)  # 512K
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated) == 4)


class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):
    def test_version(self):
        args = [
            "--config_path=" + tempfile.mktemp(),
            "version"
        ]
        self.assertTrue(cli.main(args))

    def test_poll(self):
        path = tempfile.mktemp()

        args = [
            "--url=" + url,
            "--config_path=" + path,
            "register",
        ]
        cli.main(args)

        args = [
            "--url=" + url,
            "--config_path=" + path,
            "poll",
            "--delay=2",
            "--limit=10"
        ]
        self.assertTrue(cli.main(args))

    def test_register(self):
        args = [
            "--url=" + url,
            "--config_path=" + tempfile.mktemp(),
            "register"
        ]
        self.assertTrue(cli.main(args))

    def test_ping(self):
        config_path = tempfile.mktemp()
        args = [
            "--url=" + url,
            "--config_path=" + config_path,
            "register"
        ]
        self.assertTrue(cli.main(args))

        args = [
            "--url=" + url,
            "--config_path=" + config_path,
            "ping"
        ]
        self.assertTrue(cli.main(args))

    def test_no_command_error(self):
        def callback():
            cli.main([])

        self.assertRaises(SystemExit, callback)

    def test_input_error(self):
        def callback():
            path = tempfile.mktemp()
            cli.main([
                "--url=" + url,
                "--config_path=" + path,
                "register",
            ])
            cli.main([
                "--url=" + url,
                "--config_path=" + path,
                "poll",
                "--delay=5",
                "--limit=xyz"
            ])

        self.assertRaises(ValueError, callback)


class TestConfig(AbstractTestSetup, unittest.TestCase):
    def test_show(self):
        payout_wif = self.btctxstore.create_key()
        hwif = self.btctxstore.create_wallet()
        payout_address = self.btctxstore.get_address(payout_wif)
        client = api.Client(config_path=tempfile.mktemp())
        config = client.config(set_wallet=hwif,
                               set_payout_address=payout_address)
        self.assertEqual(config["wallet"], hwif)
        self.assertEqual(config["payout_address"], payout_address)

    def test_validation(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.config(set_payout_address="invalid")

        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_persistance(self):
        config_path = tempfile.mktemp()
        a = api.Client(config_path=config_path).config()
        b = api.Client(config_path=config_path).config()
        c = api.Client(config_path=config_path).config()
        self.assertEqual(a, b, c)
        self.assertTrue(c["wallet"] is not None)


if __name__ == '__main__':
    unittest.main()
