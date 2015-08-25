#!/usr/bin/env python3

from future.standard_library import install_aliases
install_aliases()
import json
import datetime
from datetime import timedelta
import os
import time
import base64
from btctxstore import BtcTxStore

from dataserv_client import __version__
from dataserv_client import messaging
from dataserv_client import builder
from dataserv_client import exceptions
from dataserv_client import config
from dataserv_client import common
from dataserv_client import deserialize


_now = datetime.datetime.now


class Client(object):

    def __init__(self, url=common.DEFAULT_URL, debug=False,
                 max_size=common.DEFAULT_MAX_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 config_path=common.DEFAULT_CONFIG_PATH,
                 set_wallet=None, set_payout_address=None,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        import pudb; pu.db # set break point
        self.url = url
        self.messanger = None  # lazy
        self.debug = debug
        self.btctxstore = BtcTxStore()
        self.retry_limit = deserialize.positive_integer(connection_retry_limit)
        self.retry_delay = deserialize.positive_integer(connection_retry_delay)
        self.max_size = deserialize.byte_count(max_size)

        # paths
        self.config_path = os.path.realpath(config_path)
        self._ensure_path_exists(os.path.dirname(self.config_path))
        self.store_path = os.path.realpath(store_path)
        self._ensure_path_exists(self.store_path)

        # init config
        self._init_config(set_payout_address, set_wallet)

    def _init_config(self, set_payout_address, set_wallet):
        self.config = config.get(self.btctxstore, self.config_path)
        config_updated = False

        if set_payout_address: # update payout address if requested
            self.config["payout_address"] = set_payout_address
            config_updated = True

        if set_wallet: # update wallet if requested
            self.config["wallet"] = set_wallet
            config_updated = True

        if config_updated: # save config if updated
            config.save(self.btctxstore, self.config_path, self.config)

    def _ensure_path_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _init_messanger(self):
        if self.messanger is None:
            wif = self.btctxstore.get_key(self.config["wallet"])
            self.messanger = messaging.Messaging(self.url, wif,
                                                 self.retry_limit,
                                                 self.retry_delay)

    def version(self):
        print(__version__)
        return __version__

    def register(self):
        """Attempt to register the config address."""
        self._init_messanger()
        registered = self.messanger.register(self.config["payout_address"])
        auth_addr = self.messanger.auth_address()
        if registered:
            print("Address {0} now registered on {1}.".format(auth_addr,
                                                              self.url))
        else:
            print("Failed to register address {0} on {1}.".format(auth_addr,
                                                                  self.url))
        return True

    def show_config(self):
        """Display saved config."""
        print(json.dumps(self.config, indent=2))
        return self.config

    def ping(self):
        """Attempt keep-alive with the server."""
        self._init_messanger()
        print("Pinging {0} with address {1}.".format(
            self.messanger.server_url(), self.messanger.auth_address()))
        self.messanger.ping()
        return True

    def poll(self, register_address=False, delay=common.DEFAULT_DELAY,
             limit=None):
        """TODO doc string"""
        stop_time = _now() + timedelta(seconds=int(limit)) if limit else None

        if register_address:
            self.register()

        while True:
            self.ping()

            if stop_time and _now() >= stop_time:
                return True
            time.sleep(int(delay))

    def build(self, cleanup=False, rebuild=False,
              set_height_interval=common.DEFAULT_SET_HEIGHT_INTERVAL):
        """TODO doc string"""

        self._init_messanger()
        def _on_generate_shard(height, seed, file_hash):
            first = height == 1
            set_height = (height % set_height_interval) == 0
            last = (int(self.max_size / common.SHARD_SIZE) + 1) == height
            if first or set_height or last:
                self.messanger.height(height)

        bldr = builder.Builder(self.config["payout_address"],
                               common.SHARD_SIZE, self.max_size,
                               debug=self.debug,
                               on_generate_shard=_on_generate_shard)
        generated = bldr.build(self.store_path, cleanup=cleanup,
                               rebuild=rebuild)
        height = len(generated)
        self.messanger.height(height)
        return generated
