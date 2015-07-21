import os
import unittest
import time
from multiprocessing import Process
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
    try:  # remove previous db file
        os.remove(dbpath)
    except OSError:
        pass  # file does not exist

    # create schema
    db.create_all()

    # start server
    app.run(host=host, port=int(port), debug=True)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.server = Process(target=start_test_server)
        self.server.start()
        time.sleep(5)
        print("SERVER PID:", self.server.pid)

    def tearDown(self):
        self.server.terminate()
        self.server.join()
        time.sleep(5)

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

    def test_ping_invalid_address(self):
        def callback():
            client.ping("xyz", url=url)
        self.assertRaises(client.InvalidAddress, callback)


if __name__ == '__main__':
    unittest.main()
