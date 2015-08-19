import json
import time
import unittest

from dataserv_client import cli
from dataserv_client import api
from dataserv_client import exceptions


fixtures = json.load(open("tests/fixtures.json"))
addresses = fixtures["addresses"]
url = "http://127.0.0.1:5000"


class TestClientBase(object):

    def setUp(self):
        time.sleep(2)  # avoid collision


class TestClientRegister(TestClientBase):

    def test_register(self):
        client = api.Client(addresses["alpha"], url=url)
        self.assertTrue(client.register())


class TestClientPing(TestClientBase):

    def test_ping(self):
        client = api.Client(addresses["gamma"], url=url)
        self.assertTrue(client.register())
        self.assertTrue(client.ping())


class TestClientPoll(TestClientBase):

    def test_poll(self):
        # TODO(mtlynch): Make a unit-test version of this that does not depend
        # on an actual server.
        client = api.Client(addresses["zeta"], url=url)
        self.assertTrue(client.poll(register_address=True, limit=60))


class TestClientBuild(TestClientBase):

    def test_build(self):
        # TODO(mtlynch): Make a unit-test version of this that does not depend
        # on an actual server.
        client = api.Client(addresses["pi"], url=url, debug=True,
                            max_size=1024*1024*256)  # 256MB
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated))

        client = api.Client(addresses["omicron"], url=url, debug=True,
                            max_size=1024*1024*512)  # 512MB
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated) == 4)


class TestClientCliArgs(TestClientBase):

    def test_poll(self):
        args = [
            "--address=" + addresses["eta"],
            "--url=" + url,
            "poll",
            "--register_address",
            "--delay=5",
            "--limit=60"
        ]
        self.assertTrue(cli.main(args))

    def test_register(self):
        args = ["--address=" + addresses["theta"], "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

    def test_ping(self):
        args = ["--address=" + addresses["iota"], "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

        args = ["--address=" + addresses["iota"], "--url=" + url, "ping"]
        self.assertTrue(cli.main(args))

    def test_no_command_error(self):
        with self.assertRaises(SystemExit):
            cli.main(["--address=" + addresses["lambda"]])

    def test_input_error(self):
        with self.assertRaises(ValueError):
            cli.main([
                "--address=" + addresses["mu"],
                "--url=" + url,
                "poll",
                "--register_address",
                "--delay=5",
                "--limit=xyz"
            ])

    def test_api_error(self):
        with self.assertRaises(exceptions.InvalidAddress):
            cli.main(["--address=xyz", "--url=" + url, "register"])


if __name__ == '__main__':
    unittest.main()
