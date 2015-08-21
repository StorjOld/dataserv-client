#!/usr/bin/env python3

from future.standard_library import install_aliases
install_aliases()
import datetime
from datetime import timedelta
import os
import time

from dataserv_client import __version__
from dataserv_client import api_client
from dataserv_client import builder
from dataserv_client import common
from dataserv_client import deserialize


_now = datetime.datetime.now


class Client(object):

    def __init__(self, wif=None, url=common.DEFAULT_URL, debug=False,
                 max_size=common.DEFAULT_MAX_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):
        retry_limit = deserialize.positive_integer(
            connection_retry_limit)
        retry_delay = deserialize.positive_integer(
            connection_retry_delay)
        self._api_client = api_client.ApiClient(url, wif, retry_limit,
                                                retry_delay)

        self.debug = debug  # TODO validate
        self.max_size = deserialize.byte_count(max_size)
        self.store_path = os.path.realpath(store_path)

        # ensure storage dir exists
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)

    def version(self):
        print(__version__)
        return __version__

    def register(self):
        """Attempt to register the config address."""
        self._api_client.register()
        print("Address {0} now registered on {1}.".format(
            self._api_client.client_address(), self._api_client.server_url()))
        return True

    def ping(self):
        """Attempt keep-alive with the server."""
        print("Pinging {0} with address {1}.".format(
            self._api_client.server_url(), self._api_client.client_address()))
        self._api_client.ping()
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

        def _on_generate_shard(height, seed, file_hash):
            first = height == 1
            set_height = (height % set_height_interval) == 0
            last = (int(self.max_size / common.SHARD_SIZE) + 1) == height
            if first or set_height or last:
                self._api_client.height(height)

        bldr = builder.Builder(self.address, common.SHARD_SIZE, self.max_size,
                               on_generate_shard=_on_generate_shard)
        generated = bldr.build(self.store_path, debug=self.debug,
                               cleanup=cleanup, rebuild=rebuild)
        height = len(generated)
        self._api_client.height(height)
        return generated
