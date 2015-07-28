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


class TestClient(unittest.TestCase):

    def setUp(self):
        try:  # remove previous db file
            os.remove(dbpath)
        except OSError:
            pass  # file does not exist

        self.server = Process(target=start_test_server)
        self.server.start()
        time.sleep(30)

    def tearDown(self):
        self.server.terminate()
        self.server.join()
        time.sleep(10)

    def test_register(self):
        self.assertTrue(client.register(address_alpha, url=url))

    def test_already_registered(self):
        def callback():
            client.register(address_beta, url=url)
            client.register(address_beta, url=url)
        self.assertRaises(client.AddressAlreadyRegistered, callback)

    def test_register_invalid_address(self):
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

    def test_ping_invalid_address(self):
        def callback():
            client.ping("xyz", url=url)
        self.assertRaises(client.InvalidAddress, callback)


if __name__ == '__main__':
    freeze_support()  # because python setup.py test ...
    unittest.main()
