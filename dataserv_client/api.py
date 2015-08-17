#!/usr/bin/env python3


from future.standard_library import install_aliases
install_aliases()


import os
import time
import urllib
import urllib.error
import urllib.request
import datetime
from http.client import HTTPException
from dataserv_client import exceptions
from dataserv_client import common
from dataserv_client import builder
from dataserv_client import deserialize
from dataserv_client import __version__


_timedelta = datetime.timedelta
_now = datetime.datetime.now


class Client(object):

    def __init__(self, address=None, url=common.DEFAULT_URL, debug=False,
                 max_size=common.DEFAULT_MAX_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        self.url = url
        self.debug = debug
        self.address = address
        self.max_size = deserialize.byte_count(max_size)
        self.store_path = os.path.realpath(store_path)

        if int(connection_retry_limit) < 0:
            raise exceptions.InvalidArgument()
        self.connection_retry_limit = int(connection_retry_limit)

        if int(connection_retry_delay) < 0:
            raise exceptions.InvalidArgument()
        self.connection_retry_delay = int(connection_retry_delay)

        # ensure storage dir exists
        self._mkdir_recursive(self.store_path)

    def _mkdir_recursive(self, path):
        sub_path = os.path.dirname(path)
        if not os.path.exists(sub_path):
            self._mkdir_recursive(sub_path)
        if not os.path.exists(path):
            os.mkdir(path)

    def _ensure_address_given(self):
        if not self.address:  # TODO ensure address is valid
            raise exceptions.AddressRequired()

    def version(self):
        print(__version__)
        return __version__

    def _url_query(self, api_call, retries=0):
        try:
            if self.debug:
                print("Query url: " + self.url + api_call)
            response = urllib.request.urlopen(self.url + api_call)
            if response.code == 200:
                return True
            return False  # pragma: no cover

        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise exceptions.AddressAlreadyRegistered(self.address,
                                                          self.url)
            elif e.code == 404:
                raise exceptions.FarmerNotFound(self.url)
            elif e.code == 400:
                raise exceptions.InvalidAddress(self.address)
            elif e.code == 500:  # pragma: no cover
                raise exceptions.FarmerError(self.url)  # pragma: no cover
            else:
                raise e  # pragma: no cover
        except HTTPException:
            self._handle_connection_error(api_call, retries)
        except urllib.error.URLError:
            self._handle_connection_error(api_call, retries)

    def _handle_connection_error(self, api_call, retries):
        if retries >= self.connection_retry_limit:
            raise exceptions.ConnectionError(self.url)
        time.sleep(self.connection_retry_delay)
        return self._url_query(api_call, retries + 1)

    def register(self):
        """Attempt to register the config address."""
        self._ensure_address_given()
        registered = self._url_query("/api/register/{0}".format(self.address))
        if registered:
            print("Address {0} now registered on {1}.".format(self.address,
                                                              self.url))
        return registered

    def ping(self):
        """Attempt keep-alive with the server."""
        self._ensure_address_given()
        print("Pinging {0} with address {1}.".format(self.url, self.address))
        return self._url_query("/api/ping/{0}".format(self.address))

    def poll(self, register_address=False, delay=common.DEFAULT_DELAY,
             limit=None):
        """TODO doc string"""
        self._ensure_address_given()
        stop_time = _now() + _timedelta(seconds=int(limit)) if limit else None

        if register_address:
            self.register()

        while True:
            self.ping()

            if stop_time and _now() >= stop_time:
                return True
            time.sleep(int(delay))

    def build(self, cleanup=False, rebuild=False):
        """TODO doc string"""
        self._ensure_address_given()
        def on_generate_shard(height, seed, file_hash):
            self._url_query('/api/height/{0}/{1}'.format(self.address, height))
        bldr = builder.Builder(self.address, common.SHARD_SIZE, self.max_size,
                               on_generate_shard=on_generate_shard)
        generated = bldr.build(self.store_path, debug=self.debug,
                               cleanup=cleanup, rebuild=rebuild)
        height = len(generated)
        self._url_query('/api/height/{0}/{1}'.format(self.address, height))
        return generated
