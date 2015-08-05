#!/usr/bin/env python3


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
                 store_path=common.DEFAULT_STORE_PATH):
        self.url = url
        self.debug = debug
        self.address = address
        self.max_size = int(max_size)
        self.store_path = store_path
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

    def register(self):
        """Attempt to register the config address."""
        self._ensure_address_given()

        try:
            api_call = "{0}/api/register/{1}".format(self.url, self.address)
            response = urllib.request.urlopen(api_call)
            if response.code == 200:
                print("Address {0} now registered on {1}.".format(self.address,
                                                                  self.url))
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
            raise exceptions.ConnectionError(self.url)

    def ping(self):
        """Attempt keep-alive with the server."""
        self._ensure_address_given()
        try:
            print("Pinging {0} with address {1}.".format(self.url,
                                                         self.address))
            api_call = "{0}/api/ping/{1}".format(self.url, self.address)
            urllib.request.urlopen(api_call)
            return True

        except urllib.error.HTTPError as e:
            if e.code == 400:
                raise exceptions.InvalidAddress(self.address)
            elif e.code == 404:
                raise exceptions.FarmerNotFound(self.url)
            elif e.code == 500:  # pragma: no cover
                raise exceptions.FarmerError(self.url)  # pragma: no cover
            else:
                raise e  # pragma: no cover
        except urllib.error.URLError:
            raise exceptions.ConnectionError(self.url)

    def poll(self, register_address=False, delay=common.DEFAULT_DELAY,
             limit=None):
        """TODO doc string"""
        self._ensure_address_given()
        stop_time = _now() + _timedelta(seconds=int(limit)) if limit else None

        if(register_address):
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
        return bldr.build(self.store_path, debug=self.debug, cleanup=cleanup)

