import unittest
import datetime
import time
from dataserv_client import common
from dataserv_client import cli
from dataserv_client import api
from dataserv_client import exceptions


url = "http://127.0.0.1:5000"

address_alpha = "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm"
address_beta = "1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa"
address_gamma = "1Jd4YBQ7d8nHGe4zWfLL9EWHMkspN9JKGf"
address_delta = "16eEuTp1QERjCC8ZnGf34NvkptMifNSCti"
address_zeta = "1FHgmJkT4od36Zu3SVSzi71Kcvcs33Y1hn"
address_eta = "1wqyu7Mxz6sgmnHGzQdaSdW8zpGkViL79"
address_theta = "1AFJM5dn1iqHXtnttJJgskKwrhhajaY7iC"
address_iota = "19oWeFAWJh3WUKF9KEXdFUtwD9TQAf4gh9"
address_lambda = "17prdhkPcSJ3TC4SoSVNCAbUdr8xZrokaY"
address_mu = "1DNe4PPhr6raNbADsHABGSpm6XQi7KhSTo"
address_nu = "16Smzr8ESjdFDdfj5pVZifvSRzHhim3gAn"
address_pi = "1EdCc5bxUAsdsvuJN48gK8UteezYNC2ffU"
address_omicron = "19FfabAxmTZRCuxBvesMovz1xSfGgsmoqg"
address_kappa = "1G5UfNg2M1qExpLGDLko8cfusLQ2GvVSqK"

address_ksi = "15xu7JLwqZB9ZakrfZQJF5AJpNDwWabqwA"
address_epsilon = "1FwSLAJtpLrSQp94damzWY2nK5cEBugZfC"
address_rho = "1EYtmt5QWgwATbJvnVP9G9cDXrMcX5bHJ"
address_sigma = "12qx5eKHmtwHkrpByYBdosRwUfSfbGsqhT"
address_tau = "1MfQwmCQaLRxAAij1Xii6BxFtkVvjrHPc2"
address_upsilon = "1MwWa91KJGzctsYxE9V5iHFVp9Ub9HBarV"
address_phi = "1LRVczz1Ln1ECom7oVotEmUVLKbxofQfKS"
address_chi = "12zhPViCGssXWiUMeGuEYgqLFr1wF1MJH9"
address_psi = "1BKUVHEWRQNFF8M9TUZhsuGiQxL6rqeSi5"
address_omega = "1NJZ3jDHVM3BdBQZPyNLc8n5GLUSmW72Vn"


class AbstractTestSetup(object):

    def setUp(self):
        time.sleep(2)  # avoid collision


class TestClientRegister(AbstractTestSetup, unittest.TestCase):

    def test_register(self):
        client = api.Client(address_alpha, url=url)
        self.assertTrue(client.register())

    def test_already_registered(self):
        def callback():
            client = api.Client(address_beta, url=url)
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
            client = api.Client(address_nu, url=url + "/xyz")
            client.register()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_address_required(self):
        def callback():
            api.Client().register()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientPing(AbstractTestSetup, unittest.TestCase):

    def test_ping(self):
        client = api.Client(address_gamma, url=url)
        self.assertTrue(client.register())
        self.assertTrue(client.ping())

    def test_invalid_address(self):
        def callback():
            client = api.Client("xyz", url=url)
            client.ping()
        self.assertRaises(exceptions.InvalidAddress, callback)

    def test_invalid_farmer(self):
        def callback():
            client = api.Client(address_delta, url=url + "/xyz")
            client.ping()
        self.assertRaises(exceptions.FarmerNotFound, callback)

    def test_address_required(self):
        def callback():
            api.Client().ping()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientPoll(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        client = api.Client(address_zeta, url=url)
        self.assertTrue(client.poll(register_address=True, limit=60))

    def test_address_required(self):
        def callback():
            api.Client().poll()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientVersion(AbstractTestSetup, unittest.TestCase):

    def test_version(self):
        client = api.Client(url=url)
        self.assertEqual(client.version(), api.__version__)


class TestInvalidArgument(AbstractTestSetup, unittest.TestCase):

    def test_invalid_retry_limit(self):
        def callback():
            api.Client(connection_retry_limit=-1)
        self.assertRaises(exceptions.InvalidArgument, callback)

    def test_invalid_retry_delay(self):
        def callback():
            api.Client(connection_retry_delay=-1)
        self.assertRaises(exceptions.InvalidArgument, callback)


class TestConnectionRetry(AbstractTestSetup, unittest.TestCase):

    def test_no_retry(self):
        def callback():
            client = api.Client(address=address_kappa,
                                url="http://invalid.url",
                                connection_retry_limit=0,
                                connection_retry_delay=0)
            client.register()
        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        print("NO RETRY", after - before)
        self.assertTrue(datetime.timedelta(seconds=15) > (after - before))

    @unittest.skip("FIXME takes to long")
    def test_default_retry(self):
        def callback():
            client = api.Client(address=address_kappa,
                                url="http://invalid.url")
            client.register()
        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        print("DEFAULT RETRY", after - before)
        seconds = (
            common.DEFAULT_CONNECTION_RETRY_LIMIT *
            common.DEFAULT_CONNECTION_RETRY_DELAY
        )
        self.assertTrue(datetime.timedelta(seconds=seconds) < (after - before))


class TestClientBuild(AbstractTestSetup, unittest.TestCase):

    # TODO test default path
    # TODO test custom path
    # TODO test shard size
    # TODO test if height set
    # TODO test cleanup

    def test_build(self):
        client = api.Client(address_pi, url=url, debug=True,
                            max_size=1024*1024*256)  # 256MB
        client.register()
        height = client.build(cleanup=True)
        self.assertTrue(height == 2)

        client = api.Client(address_omicron, url=url, debug=True,
                            max_size=1024*1024*512)  # 512MB
        client.register()
        height = client.build(cleanup=True)
        self.assertTrue(height == 4)

    def test_address_required(self):
        def callback():
            api.Client().build()
        self.assertRaises(exceptions.AddressRequired, callback)


class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):

    def test_poll(self):
        args = [
            "--address=" + address_eta,
            "--url=" + url,
            "poll",
            "--register_address",
            "--delay=5",
            "--limit=60"
        ]
        self.assertTrue(cli.main(args))

    def test_register(self):
        args = ["--address=" + address_theta, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

    def test_ping(self):
        args = ["--address=" + address_iota, "--url=" + url, "register"]
        self.assertTrue(cli.main(args))

        args = ["--address=" + address_iota, "--url=" + url, "ping"]
        self.assertTrue(cli.main(args))

    def test_no_command_error(self):
        def callback():
            cli.main(["--address=" + address_lambda])
        self.assertRaises(SystemExit, callback)

    def test_input_error(self):
        def callback():
            cli.main([
                "--address=" + address_mu,
                "--url=" + url,
                "poll",
                "--register_address",
                "--delay=5",
                "--limit=xyz"
            ])
        self.assertRaises(ValueError, callback)

    def test_api_error(self):
        def callback():
            cli.main(["--address=xyz", "--url=" + url, "register"])
        self.assertRaises(exceptions.InvalidAddress, callback)


if __name__ == '__main__':
    unittest.main()
