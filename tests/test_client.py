import os
import unittest
import time
from multiprocessing import Process, freeze_support
from dataserv_client import cli
from dataserv_client import client
from dataserv_client import exceptions
import dataserv
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
        api = client.ClientApi(address_alpha, url=url)
        self.assertTrue(api.register())

    def test_already_registered(self):
        def callback():
            api = client.ClientApi(address_alpha, url=url)
            api.register()
            api.register()
        self.assertRaises(exceptions.AddressAlreadyRegistered, callback)

    def test_invalid_address(self):
        def callback():
            api = client.ClientApi("xyz", url=url)
            api.register()
        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            api = client.ClientApi(address_beta, url=url + "/xyz")
            api.register()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            api = client.ClientApi(address_beta, url="http://doesnt.exist.com")
            api.register()
        self.assertRaises(exceptions.ConnectionError, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):

    def test_ping(self):
        api = client.ClientApi(address_alpha, url=url)
        self.assertTrue(api.register())
        self.assertTrue(api.ping())

    def test_invalid_address(self):
        def callback():
            api = client.ClientApi("xyz", url=url)
            api.ping()
        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            api = client.ClientApi(address_alpha, url=url + "/xyz")
            api.ping()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            api = client.ClientApi(address_alpha,
                                   url="http://doesnt.exist.com")
            api.ping()
        self.assertRaises(exceptions.ConnectionError, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        api = client.ClientApi(address_alpha, url=url)
        self.assertTrue(api.poll(register_address=True, limit=60))


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

    def test_client_error(self):
        args = ["xyz", "--url=" + url, "register"]
        self.assertTrue(cli.main(args) is None)


if __name__ == '__main__':
    freeze_support()  # for windows ...
    unittest.main()
