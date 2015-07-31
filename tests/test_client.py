import os
import unittest
import time
import dataserv
from multiprocessing import Process, freeze_support
from dataserv_client import cli
from dataserv_client import api
from dataserv_client import exceptions
from dataserv.app import app, db


port = "5000"
host = "127.0.0.1"
url = "http://%s:%s" % (host, port)
dbpath = os.path.join(os.path.dirname(dataserv.__file__), 'dataserv.db')
address_alpha = "13wENBbYbNW9KczZSQXyVogzB15jyVmmKS"
address_beta = "15JPEyzUgBKYJSrtHQ9g5kVbm8hghLhv1b"
address_gamma = "1DauYnqSjZbRSfUoderYgTLdjCjBuyENWA"


class AbstractTestSetup(object):

    def setUp(self):
        # remove previous db file
        try:
            os.remove(dbpath)
        except OSError:
            pass  # file does not exist

        def start_test_server():
            db.create_all()  # create schema
            app.run(host=host, port=int(port), debug=True)  # start server

        self.server = Process(target=start_test_server)
        self.server.start()
        time.sleep(5)

    def tearDown(self):
        self.server.terminate()
        self.server.join()
        time.sleep(1)


class TestClientRegister(AbstractTestSetup, unittest.TestCase):

    def test_register(self):
        client = api.Client(address_alpha, url=url)
        self.assertTrue(client.register())

    def test_already_registered(self):
        def callback():
            client = api.Client(address_alpha, url=url)
            client.register()
            client.register()
        self.assertRaises(exceptions.AddressAlreadyRegistered, callback)

    def test_invalid_address(self):
        def callback():
            client = api.Client("xyz", url=url)
            client.register()
        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            client = api.Client(address_beta, url=url + "/xyz")
            client.register()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            client = api.Client(address_beta, url="http://doesnt.exist.com")
            client.register()
        self.assertRaises(exceptions.ConnectionError, callback)

    def test_address_required(self):
        def callback():
            api.Client().register()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):

    def test_ping(self):
        client = api.Client(address_alpha, url=url)
        self.assertTrue(client.register())
        self.assertTrue(client.ping())

    def test_invalid_address(self):
        def callback():
            client = api.Client("xyz", url=url)
            client.ping()
        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            client = api.Client(address_alpha, url=url + "/xyz")
            client.ping()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            client = api.Client(address_alpha, url="http://doesnt.exist.com")
            client.ping()
        self.assertRaises(exceptions.ConnectionError, callback)

    def test_address_required(self):
        def callback():
            api.Client().ping()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        client = api.Client(address_alpha, url=url)
        self.assertTrue(client.poll(register_address=True, limit=60))

    def test_address_required(self):
        def callback():
            api.Client().poll()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientVersion(AbstractTestSetup, unittest.TestCase):

    def test_version(self):
        client = api.Client(url=url)
        self.assertEqual(client.version(), api.__version__)


class TestClientBuild(AbstractTestSetup, unittest.TestCase):

    def test_build(self):
        client = api.Client(address_alpha, url=url, debug=True,
                            max_size=1024*1024*256)  # 256MB
        hashes = client.build(cleanup=True)
        self.assertTrue(len(hashes) == 2)

        client = api.Client(address_alpha, url=url, debug=True,
                            max_size=1024*1024*512)  # 512MB
        hashes = client.build(cleanup=True)
        self.assertTrue(len(hashes) == 4)

    def test_address_required(self):
        def callback():
            api.Client().build()
        self.assertRaises(exceptions.AddressRequired, callback)

class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        args = [
            address_alpha,
            "--url=" + url,
            "poll",
            "--register_address",
            "--delay=5",
            "--limit=60"
        ]
        self.assertTrue(cli.main(args))

    def test_register(self):
        args = [address_alpha, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

    def test_ping(self):
        args = [address_alpha, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

        args = [address_alpha, "--url=" + url, "ping"]
        self.assertTrue(cli.main(args))

    def test_no_command_error(self):
        def callback():
            cli.main([address_alpha])
        self.assertRaises(SystemExit, callback)

    def test_input_error(self):
        def callback():
            cli.main([
                address_alpha,
                "--url=" + url,
                "poll",
                "--register_address",
                "--delay=5",
                "--limit=xyz"
            ])
        self.assertRaises(ValueError, callback)

    def test_api_error(self):
        def callback():
            cli.main(["xyz", "--url=" + url, "register"])
        self.assertRaises(exceptions.InvalidAddress, callback)


if __name__ == '__main__':
    freeze_support()  # for windows ...
    unittest.main()
