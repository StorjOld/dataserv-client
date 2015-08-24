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
                 set_master_secret=None, set_payout_address=None,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        # FIXME validate payout_address
        # FIXME validate master_secret
        self.btctxstore = BtcTxStore()
        self.url = url
        self.config = None  # lazy
        self.messanger = None  # lazy
        self.debug = debug  # TODO validate
        self.retry_limit = deserialize.positive_integer(connection_retry_limit)
        self.retry_delay = deserialize.positive_integer(connection_retry_delay)
        self.max_size = deserialize.byte_count(max_size)

        # paths
        self.config_path = os.path.realpath(config_path)  # TODO validate
        self._ensure_path_exists(os.path.dirname(self.config_path))
        self.store_path = os.path.realpath(store_path)
        self._ensure_path_exists(self.store_path)

        self._initialize_config(set_master_secret, set_payout_address)

    def _initialize_config(self, set_master_secret, set_payout_address):
        if os.path.exists(self.config_path):
            self._load_config()
        else:  # initialize config
            if not set_master_secret:  # create random master secret
                secret_data = base64.b64encode(os.urandom(256))
                set_master_secret = secret_data.decode('utf-8')
            if not set_payout_address:  # use root address if not given
                set_payout_address = self._get_root_address(set_master_secret)

        if set_master_secret or set_payout_address:
            self.config = {
                "master_secret": set_master_secret,
                "payout_address": set_payout_address,
            }
            config.save(self.config_path, self.config)

    def _ensure_path_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _load_config(self):
        if self.config is None:
            if not os.path.exists(self.config_path):
                raise exceptions.ConfigNotFound(self.config_path)
            self.config = config.load(self.config_path)

    def _get_root_wif(self, master_secret):
        master_secret = base64.b64decode(master_secret)
        hwif = self.btctxstore.create_wallet(master_secret=master_secret)
        return self.btctxstore.get_key(hwif)

    def _get_root_address(self, master_secret):
            wif = self._get_root_wif(master_secret)
            return self.btctxstore.get_address(wif)

    def _init_messanger(self):
        if self.messanger is None:
            self._load_config()
            wif = self._get_root_wif(self.config["master_secret"])
            self.messanger = messaging.Messaging(self.url, wif,
                                                 self.retry_limit,
                                                 self.retry_delay)

    def version(self):
        print(__version__)
        return __version__

    def register(self):
        """Attempt to register the config address."""
        self._load_config()
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
