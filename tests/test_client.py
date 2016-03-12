from dataserv_client import common
import os
import tempfile
import unittest
import datetime
import json
import psutil
from future.moves.urllib.request import urlopen
from dataserv_client import cli
from dataserv_client import api
from btctxstore import BtcTxStore
from dataserv_client import exceptions


url = "http://127.0.0.1:5000"
common.SHARD_SIZE = 1024 * 128  # monkey patch shard size to 128K


class AbstractTestSetup(object):
    def setUp(self):
        self.btctxstore = BtcTxStore()

        # debug output the server online list
        # print(urlopen(url + '/api/online/json').read().decode('utf8'))


class TestClientRegister(AbstractTestSetup, unittest.TestCase):

    def test_register_payout(self):
        client = api.Client(url=url, config_path=tempfile.mktemp())
        config = client.config()
        self.assertTrue(client.register())
        result = json.loads(
            urlopen(url + '/api/online/json').read().decode('utf8')
        )
        result = [farmer for farmer in result['farmers']
                  if farmer['payout_addr'] == config['payout_address']]
        last_seen = result[0]['last_seen']
        reg_time = result[0]['reg_time']
        result = json.dumps(result, sort_keys=True)
        expected = json.dumps([{
            'height': 0,
            'nodeid': common.address2nodeid(config['payout_address']),
            'last_seen': last_seen,
            'payout_addr': config['payout_address'],
            'reg_time': reg_time,
            'bandwidth_upload': 0,
            'bandwidth_download': 0,
            "ip": "",
            'uptime': 100.0
        }], sort_keys=True)
        self.assertEqual(result, expected)

    def test_register(self):  # register without createing a config
        client = api.Client(url=url)
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

        before = datetime.datetime.now()
        self.assertTrue(client.poll(delay=2, limit=2))
        after = datetime.datetime.now()

        # check that poll did 2 pings with 2 sec delay
        self.assertTrue(datetime.timedelta(seconds=2) <= (after - before))


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

    def test_invalid_negativ_min_free_size(self):
        def callback():
            api.Client(min_free_size=-1, config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_invalid_zero_min_free_size(self):
        def callback():
            api.Client(min_free_size=0, config_path=tempfile.mktemp())

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_build_invalid_negative_workers(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.build(workers=-1)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_farm_invalid_zero_workers(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.farm(workers=0)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_build_invalid_negative_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.build(set_height_interval=-1)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_farm_invalid_zero_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.farm(set_height_interval=0)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_farm_invalid_negative_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.farm(set_height_interval=-1)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_build_invalid_zero_set_height_interval(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.build(set_height_interval=0)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_poll_invalid_negativ_delay(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.poll(delay=-1, limit=0)

        self.assertRaises(exceptions.InvalidInput, callback)

    def test_audit_invalid_negativ_delay(self):
        def callback():
            client = api.Client(config_path=tempfile.mktemp())
            client.audit(delay=-1, limit=0)

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

    def test_retry_server_not_found(self):
        def callback():
            client = api.Client(url="http://ServerNotFound.url",
                                config_path=tempfile.mktemp(),
                                connection_retry_limit=2,
                                connection_retry_delay=2)
            client.register()

        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=4) < (after - before))

    def test_retry_invalid_url(self):
        def callback():
            client = api.Client(url="http://127.0.0.257",
                                config_path=tempfile.mktemp(),
                                connection_retry_limit=2,
                                connection_retry_delay=2)
            client.register()

        before = datetime.datetime.now()
        self.assertRaises(exceptions.ConnectionError, callback)
        after = datetime.datetime.now()
        self.assertTrue(datetime.timedelta(seconds=4) < (after - before))

    def test_retry_high_retry_limit(self):
        def callback():
            client = api.Client(url="http://127.0.0.257",
                                config_path=tempfile.mktemp(),
                                connection_retry_limit=2000,
                                connection_retry_delay=0,
                                quiet=True)
            client.register()

        self.assertRaises(exceptions.ConnectionError, callback)


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
        config = client.config()
        client.register()
        generated = client.build(cleanup=True)
        self.assertTrue(len(generated) == 4)

        result = json.loads(
            urlopen(url + '/api/online/json').read().decode('utf8')
        )
        result = [farmer for farmer in result['farmers']
                  if farmer['payout_addr'] == config['payout_address']]

        last_seen = result[0]['last_seen']
        reg_time = result[0]['reg_time']
        result = json.dumps(result, sort_keys=True)
        expected = json.dumps([{
            'height': 4,
            'nodeid': common.address2nodeid(config['payout_address']),
            'last_seen': last_seen,
            'payout_addr': config['payout_address'],
            'reg_time': reg_time,
            'bandwidth_upload': 0,
            'bandwidth_download': 0,
            "ip": "",
            'uptime': 100.0
        }], sort_keys=True)
        self.assertEqual(result, expected)

    def test_build_min_free_space(self):

        store_path = tempfile.mktemp()
        os.mkdir(store_path)
        my_free_size = psutil.disk_usage(store_path).free - (1024 * 256)  # 256
        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            store_path=store_path,
                            max_size=1024 * 1024 * 2,
                            min_free_size=my_free_size)  # 256
        config = client.config()
        client.register()
        generated = client.build()
        self.assertTrue(len(generated) > 0)  # build at least 1 shard
        self.assertTrue(len(generated) < 16)  # stoped cause of free Space

        result = json.loads(
            urlopen(url + '/api/online/json').read().decode('utf8')
        )
        result = [farmer for farmer in result['farmers']
                  if farmer['payout_addr'] == config['payout_address']]
        last_seen = result[0]['last_seen']
        reg_time = result[0]['reg_time']
        result = json.dumps(result, sort_keys=True)
        expected = json.dumps([{
            'height': len(generated),
            'nodeid': common.address2nodeid(config['payout_address']),
            'last_seen': last_seen,
            'payout_addr': config['payout_address'],
            'reg_time': reg_time,
            'bandwidth_upload': 0,
            'bandwidth_download': 0,
            "ip": "",
            'uptime': 100.0
        }], sort_keys=True)

        self.assertEqual(result, expected)


class TestClientFarm(AbstractTestSetup, unittest.TestCase):
    def test_farm(self):
        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            max_size=1024 * 256)  # 256K

        befor = datetime.datetime.now()
        self.assertTrue(client.farm(delay=2, limit=2))  # check farm return true
        after = datetime.datetime.now()

        # check that farm did 2 pings with 2 sec delay
        self.assertTrue(datetime.timedelta(seconds=2) <= (after - befor))

    def test_farm_registered(self):
        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            max_size=1024 * 256)  # 256K
        config = client.config()
        client.register()

        befor = datetime.datetime.now()
        self.assertTrue(client.farm(delay=2, limit=2))  # check farm return true
        after = datetime.datetime.now()

        # check that farm did 2 pings with 2 sec delay
        self.assertTrue(datetime.timedelta(seconds=2) <= (after - befor))

        result = json.loads(
            urlopen(url + '/api/online/json').read().decode('utf8')
        )
        result = [farmer for farmer in result['farmers']
                  if farmer['payout_addr'] == config['payout_address']]
        last_seen = result[0]['last_seen']
        reg_time = result[0]['reg_time']

        bandwidth_upload = result.pop('bandwidth_upload')
        bandwidth_download = result.pop('bandwidth_download')
        self.assertGreater(bandwidth_upload, 0)
        self.assertGreater(bandwidth_download, 0)

        result = json.dumps(result, sort_keys=True)
        expected = json.dumps([{
            'height': 2,
            'nodeid': common.address2nodeid(config['payout_address']),
            'last_seen': last_seen,
            'payout_addr': config['payout_address'],
            'reg_time': reg_time,
            "ip": "",
            'uptime': 100.0
        }], sort_keys=True)

        self.assertEqual(result, expected)


class TestClientAudit(AbstractTestSetup, unittest.TestCase):
    @unittest.skip("to many blockchain api requests")
    def test_audit(self):
        client = api.Client(url=url,
                            config_path=tempfile.mktemp(),
                            max_size=1024 * 256)  # 256K
        client.register()
        self.assertTrue(client.audit(delay=1, limit=1))


class TestClientCliArgs(AbstractTestSetup, unittest.TestCase):
    def test_version(self):
        args = [
            "--config_path=" + tempfile.mktemp(),
            "version"
        ]
        self.assertTrue(cli.main(args))

    def test_freespace(self):
        args = [
            "--config_path=" + tempfile.mktemp(),
            "freespace"
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
            "--delay=0",
            "--limit=0"
        ]  # no pings needed for check args
        self.assertTrue(cli.main(args))

    def test_register(self):
        args = [
            "--url=" + url,
            "--config_path=" + tempfile.mktemp(),
            "register"
        ]
        self.assertTrue(cli.main(args))

    def test_build(self):
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
            "--max_size=" + str(1024 * 256),  # 256K
            "--min_free_size=" + str(1024 * 256),  # 256K
            "build",
            "--workers=4",
            "--cleanup",
            "--rebuild",
            "--repair",
            "--set_height_interval=3"
        ]
        self.assertTrue(cli.main(args))

    def test_audit(self):
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
            "audit",
            "--delay=0",
            "--limit=0"
        ]  # no audit needed for check args
        self.assertTrue(cli.main(args))

    def test_farm(self):
        args = [
            "--url=" + url,
            "--config_path=" + tempfile.mktemp(),
            "--max_size=" + str(1024 * 256),  # 256K
            "--min_free_size=" + str(1024 * 256),  # 256K
            "farm",
            "--workers=4",
            "--cleanup",
            "--rebuild",
            "--repair",
            "--set_height_interval=3",
            "--delay=0",
            "--limit=0"
        ]  # no pings needed for check args
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
