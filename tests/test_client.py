import os
import unittest
import time
from multiprocessing import Process, freeze_support
from dataserv_client import client
import dataserv
from dataserv.app import app, db


port = "5000"
host = "127.0.0.1"
url = "http://%s:%s" % (host, port)
dbpath = os.path.join(os.path.dirname(dataserv.__file__), 'dataserv.db')
address_alpha = "13wENBbYbNW9KczZSQXyVogzB15jyVmmKS"
address_beta = "15JPEyzUgBKYJSrtHQ9g5kVbm8hghLhv1b"
address_gamma = "1DauYnqSjZbRSfUoderYgTLdjCjBuyENWA"


def start_test_server():
    db.create_all()  # create schema
    app.run(host=host, port=int(port), debug=True)  # start server


class AbstractTestSetup(object):

    def setUp(self):
        try:  # remove previous db file
            os.remove(dbpath)
        except OSError:
            pass  # file does not exist

        self.server = Process(target=start_test_server)
        self.server.start()
        time.sleep(15)

    def tearDown(self):
        self.server.terminate()
        self.server.join()
        time.sleep(5)


class TestClientRegister(AbstractTestSetup, unittest.TestCase):

    def test_register(self):
        self.assertTrue(client.register(address_alpha, url=url))

    def test_already_registered(self):
        def callback():
            client.register(address_beta, url=url)
            client.register(address_beta, url=url)
        self.assertRaises(client.AddressAlreadyRegistered, callback)

    def test_invalid_address(self):
        def callback():
            client.register("xyz", url=url)
        self.assertRaises(client.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            client.register(address_beta, url=url + "/xyz")
        self.assertRaises(client.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            client.register(address_beta, url="http://doesnt.exist.com")
        self.assertRaises(client.ConnectionError, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):

    def test_ping(self):
        self.assertTrue(client.register(address_alpha, url=url))
        self.assertTrue(client.ping(address_alpha, url=url))

    def test_invalid_address(self):
        def callback():
            client.ping("xyz", url=url)
        self.assertRaises(client.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            client.ping(address_alpha, url=url + "/xyz")
        self.assertRaises(client.FarmerNotFound, callback)

    def test_connection_error(self):
        def callback():
            client.ping(address_alpha, url="http://doesnt.exist.com")
        self.assertRaises(client.ConnectionError, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        self.assertTrue(client.poll(address_alpha, register_address=True,
                                    url=url, limit=60))


class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        args = [
            "poll", 
            address_alpha, 
            "--register_address",
            "--delay=5",
            "--url=" + url,
            "--limit=60" 
        ]
        self.assertTrue(client.main(args))

    def test_register(self):
        args = [ "register", address_alpha, "--url=" + url ]
        self.assertTrue(client.main(args))

    def test_ping(self):
        args = [ "register", address_alpha, "--url=" + url ]
        self.assertTrue(client.main(args))

        args = [ "ping", address_alpha, "--url=" + url ]
        self.assertTrue(client.main(args))


if __name__ == '__main__':
    freeze_support()  # because python setup.py test ...
    unittest.main()
