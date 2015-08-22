import json
import time
import unittest
import datetime
from btctxstore import BtcTxStore
from dataserv_client import cli
from dataserv_client import api
from dataserv_client import exceptions


url = "http://127.0.0.1:5000"


class AbstractTestSetup(object):

    def setUp(self):
        self.btctxstore = BtcTxStore()
        time.sleep(2)  # avoid collision


class TestClientRegister(AbstractTestSetup, unittest.TestCase):

    def test_register(self):
        wif = self.btctxstore.create_key()
        client = api.Client(wif, url=url, debug=True)
        self.assertTrue(client.register())

    def test_already_registered(self):
        def callback():
            wif = self.btctxstore.create_key()
            client = api.Client(wif, url=url, debug=True)
            client.register()
            client.register()
        self.assertRaises(exceptions.AddressAlreadyRegistered, callback)

    def test_invalid_wif(self):
        def callback():
            client = api.Client("xyz", url=url, debug=True)
            client.register()
        self.assertRaises(exceptions.InvalidWif, callback)

    def test_invalid_farmer(self):
        def callback():
            wif = self.btctxstore.create_key()
            client = api.Client(wif, url=url + "/xyz", debug=True)
            client.register()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_address_required(self):
        def callback():
            api.Client(debug=True).register()
        self.assertRaises(exceptions.AuthWifRequired, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):

    def test_ping(self):
        wif = self.btctxstore.create_key()
        client = api.Client(wif, url=url, debug=True)
        self.assertTrue(client.register())
        self.assertTrue(client.ping())

    def test_invalid_wif(self):
        def callback():
            client = api.Client("xyz", url=url, debug=True)
            client.ping()
        self.assertRaises(exceptions.InvalidWif, callback)

    def test_invalid_farmer(self):
        def callback():
            wif = self.btctxstore.create_key()
            client = api.Client(wif, url=url + "/xyz", debug=True)
            client.ping()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_address_required(self):
        def callback():
            api.Client(debug=True).ping()
        self.assertRaises(exceptions.AuthWifRequired, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        wif = self.btctxstore.create_key()
        client = api.Client(wif, url=url, debug=True)
        self.assertTrue(client.poll(register_address=True, limit=60))

    def test_address_required(self):
        def callback():
            api.Client(debug=True).poll()
        self.assertRaises(exceptions.AuthWifRequired, callback)


class TestInvalidArgument(AbstractTestSetup, unittest.TestCase):

    def test_invalid_retry_limit(self):
        def callback():
            api.Client(connection_retry_limit=-1, debug=True)
        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_retry_delay(self):
        def callback():
            api.Client(connection_retry_delay=-1, debug=True)
        self.assertRaises(exceptions.InvalidInput, callback)


class TestConnectionRetry(AbstractTestSetup, unittest.TestCase):

    def test_no_retry(self):
        def callback():
            wif = self.btctxstore.create_key()
            client = api.Client(wif=wif, url="http://invalid.url",
                                connection_retry_limit=0,
                                connection_retry_delay=0, debug=True)
            client.register()
        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=15) > (after - before))

    def test_default_retry(self):
        def callback():
            wif = self.btctxstore.create_key()
            client = api.Client(wif=wif, url="http://invalid.url",
                                connection_retry_limit=5,
                                connection_retry_delay=5, debug=True)
            client.register()
        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=25) < (after - before))


class TestClientBuild(AbstractTestSetup, unittest.TestCase):

    def test_build(self):
        wif = self.btctxstore.create_key()
        client = api.Client(wif, url=url, debug=True,
                            max_size=1024*1024*256)  # 256MB
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated))

        wif = self.btctxstore.create_key()
        client = api.Client(wif, url=url, debug=True,
                            max_size=1024*1024*512)  # 512MB
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated) == 4)

    def test_address_required(self):
        def callback():
            api.Client(debug=True).build()
        self.assertRaises(exceptions.AuthWifRequired, callback)


class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):

    def test_version(self):
        self.assertTrue(cli.main(["version"]))

    def test_poll(self):
        wif = self.btctxstore.create_key()
        args = [
            "--wif=" + wif,
            "--url=" + url,
            "poll",
            "--register_address",
            "--delay=5",
            "--limit=60"
        ]
        self.assertTrue(cli.main(args))

    def test_register(self):
        wif = self.btctxstore.create_key()
        args = ["--wif=" + wif, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

    def test_ping(self):
        wif = self.btctxstore.create_key()
        args = ["--wif=" + wif, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

        args = ["--wif=" + wif, "--url=" + url, "ping"]
        self.assertTrue(cli.main(args))

    def test_no_command_error(self):
        def callback():
            wif = self.btctxstore.create_key()
            cli.main(["--wif=" + wif])
        self.assertRaises(SystemExit, callback)

    def test_input_error(self):
        def callback():
            wif = self.btctxstore.create_key()
            cli.main([
                "--wif=" + wif,
                "--url=" + url,
                "poll",
                "--register_address",
                "--delay=5",
                "--limit=xyz"
            ])
        self.assertRaises(ValueError, callback)

    def test_api_error(self):
        def callback():
            cli.main(["--wif=xyz", "--url=" + url, "register"])
        self.assertRaises(exceptions.InvalidWif, callback)


if __name__ == '__main__':
    unittest.main()
