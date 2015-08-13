#!/usr/bin/env python3


from future.standard_library import install_aliases
install_aliases()


import os
import time
import urllib
import urllib.error
import urllib.request
import datetime
from dataserv_client import exceptions
from dataserv_client import common
from dataserv_client import builder
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
        self.max_size = int(max_size)
        self.store_path = store_path

        if int(connection_retry_limit) < 0:
            raise exceptions.InvalidArgument()
        self.connection_retry_limit = int(connection_retry_limit)

        if int(connection_retry_delay) < 0:
            raise exceptions.InvalidArgument()
        self.connection_retry_delay = int(connection_retry_delay)

        # ensure storage dir exists
        self._mkdir_recursive(store_path)

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

    def _querry(self, api_call, retries=0):
        try:
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
        except urllib.error.URLError:
            if retries >= self.connection_retry_limit:
                raise exceptions.ConnectionError(self.url)
            time.sleep(self.connection_retry_delay)
            return self._querry(api_call, retries + 1)

    def register(self):
        """Attempt to register the config address."""
        self._ensure_address_given()
        registered = self._querry("/api/register/{0}".format(self.address))
        if registered:
            print("Address {0} now registered on {1}.".format(self.address,
                                                              self.url))
        return registered

    def ping(self):
        """Attempt keep-alive with the server."""
        self._ensure_address_given()
        print("Pinging {0} with address {1}.".format(self.url, self.address))
        return self._querry("/api/ping/{0}".format(self.address))

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

    def build(self, cleanup=False):
        """TODO doc string"""
        self._ensure_address_given()
        bldr = builder.Builder(self.address, common.SHARD_SIZE, self.max_size)
        hashes = bldr.build(self.store_path, debug=self.debug, cleanup=cleanup)
        self._querry('/api/height/{0}/{1}'.format(self.address, len(hashes)))
        return hashes
