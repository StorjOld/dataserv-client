#!/usr/bin/env python3

from future.standard_library import install_aliases
install_aliases()

import os
import time
import json
from datetime import datetime
from datetime import timedelta
from btctxstore import BtcTxStore
from dataserv_client import config
from dataserv_client import common
from dataserv_client import builder
from dataserv_client import messaging
from dataserv_client import deserialize
from dataserv_client import __version__


SHOW_CONFIG_TEMPLATE = """Current configuration.

    Authentication address: {0}
    Payout address: {0}
"""


class Client(object):

    def __init__(self, url=common.DEFAULT_URL, debug=False,
                 max_size=common.DEFAULT_MAX_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 config_path=common.DEFAULT_CONFIG_PATH,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        self.url = url
        self.debug = debug
        self.max_size = deserialize.byte_count(max_size)

        self.messenger = None  # lazy
        self.btctxstore = BtcTxStore()
        self.retry_limit = deserialize.positive_integer(connection_retry_limit)
        self.retry_delay = deserialize.positive_integer(connection_retry_delay)

        # paths
        self.cfg_path = os.path.realpath(config_path)
        self._ensure_path_exists(os.path.dirname(self.cfg_path))
        self.store_path = os.path.realpath(store_path)
        self._ensure_path_exists(self.store_path)

        self.cfg = config.get(self.btctxstore, self.cfg_path)

    @staticmethod
    def version():
        print(__version__)
        return __version__

    @staticmethod
    def _ensure_path_exists(path):
        """To keep front writing to non-existant paths."""
        if not os.path.exists(path):
            os.makedirs(path)

    def _init_messenger(self):
        """Make sure messenger exists."""
        if self.messenger is None:
            wif = self.btctxstore.get_key(self.cfg["wallet"])
            self.messenger = messaging.Messaging(self.url, wif,
                                                 self.retry_limit,
                                                 self.retry_delay,
                                                 debug=self.debug)

    def register(self):
        """Attempt to register the config address."""
        self._init_messenger()
        payout_address = self.cfg["payout_address"]
        self.messenger.register(payout_address)
        print("Registered on server '{0}'.".format(self.url))

    def config(self, set_wallet=None, set_payout_address=None):
        """
        Set and then show the config settings.

        :param set_wallet: Set the HWIF for registration/auth address.
        :param set_payout_address:  Set the payout address.
        :return: Configuation object.
        """
        self._init_messenger()
        config_updated = False

        # update payout address if requested
        if set_payout_address:
            self.cfg["payout_address"] = set_payout_address
            config_updated = True

        # update wallet if requested
        if set_wallet:
            self.cfg["wallet"] = set_wallet
            config_updated = True

        # save config if updated
        if config_updated:
            config.save(self.btctxstore, self.cfg_path, self.cfg)

        # display config
        print(SHOW_CONFIG_TEMPLATE.format(
            self.cfg["payout_address"],
            self.messenger.auth_address(),
        ))
        return self.cfg

    def ping(self):
        """Attempt one keep-alive with the server."""
        self._init_messenger()

        msg = "Pinging server '{0}' at {1:%Y-%m-%d %H:%M:%S}."
        print(msg.format(self.messenger.server_url(), datetime.now()))
        self.messenger.ping()

        return True

    def poll(self, register_address=False, delay=common.DEFAULT_DELAY,
             limit=None):
        """
        Attempt continuous keep-alive with the server.

        :param register_address: Registration/auth Bitcoin address.
        :param delay: Delay in seconds per ping of the server.
        :param limit: Number of seconds in the future to stop polling.
        :return: True, if limit is reached. None, if otherwise.
        """
        stop_time = None
        if limit:
            stop_time = datetime.now() + timedelta(seconds=int(limit))

        if register_address:  # in case the user forgot to register
            self.register()

        while True:  # ping the server every X seconds
            self.ping()

            if stop_time and datetime.now() >= stop_time:
                return True
            time.sleep(int(delay))

    def build(self, cleanup=False, rebuild=False,
              set_height_interval=common.DEFAULT_SET_HEIGHT_INTERVAL):
        """
        Generate test files deterministically based on address.

        :param cleanup: Remove files in shard directory.
        :param rebuild: Re-generate any file shards.
        :param set_height_interval: Number of shards to generate before
                                    notifying the server.
        """

        self._init_messenger()
        print("Starting build")

        def _on_generate_shard(cur_height, cur_seed, cur_file_hash):
            """
            Because URL requests are slow, only update the server when we are
            at the first height, at some height_interval, or the last height.

            :param cur_height: Current height in the building process.
            """
            first = cur_height == 1
            set_height = (cur_height % int(set_height_interval)) == 0
            last = int(self.max_size / common.SHARD_SIZE) == cur_height

            if first or set_height or last:
                self.messenger.height(cur_height)
                print("Current height at {0}.".format(cur_height))

        # Initialize builder and generate/re-generate shards
        bldr = builder.Builder(self.cfg["payout_address"],
                               common.SHARD_SIZE, self.max_size,
                               debug=self.debug,
                               on_generate_shard=_on_generate_shard)
        generated = bldr.build(self.store_path, cleanup=cleanup,
                               rebuild=rebuild)

        print("Build finished")
        return generated

    def start(self):
        """ Fully automatic client for users wishing a simple turnkey solution.
        This will run all functions automaticly with the most sane defaults
        and as little user interface as possible.
        """
        try:
            self.register()
        except exceptions.AddressAlreadyRegistered:
            pass  # already registered ...
        self.build()
        self.poll()
