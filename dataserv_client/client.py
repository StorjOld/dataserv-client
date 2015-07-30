#!/usr/bin/env python3


import time
import urllib
import urllib.error
import urllib.request
import datetime
from dataserv_client import exceptions
from dataserv_client import cli
from dataserv_client import common


_timedelta = datetime.timedelta
_now = datetime.datetime.now


class ClientApi(object):

    def __init__(self, address, url=common.DEFAULT_URL):
        self.url = url
        self.address = address  # FIXME check it address is valid client side

    def register(self):
        """Attempt to register the config address."""

        try:
            api_call = "{0}/api/register/{1}".format(self.url, self.address)
            response = urllib.request.urlopen(api_call)
            if response.code == 200:
                print("Address {0} now registered on {1}.".format(self.address,
                                                                  self.url))
                return True
            return False

        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise exceptions.AddressAlreadyRegistered(self.address,
                                                          self.url)
            elif e.code == 404:
                raise exceptions.FarmerNotFound(self.url)
            elif e.code == 400:
                raise exceptions.InvalidAddress(self.address)
            elif e.code == 500:
                raise exceptions.FarmerError(self.url)
            else:
                raise e
        except urllib.error.URLError:
            raise exceptions.ConnectionError(self.url)

    def ping(self):
        """Attempt keep-alive with the server."""
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
            elif e.code == 500:
                raise exceptions.FarmerError(self.url)
            else:
                raise e
        except urllib.error.URLError:
            raise exceptions.ConnectionError(self.url)

    def poll(self, register_address=False, delay=common.DEFAULT_DELAY,
             limit=None):
        """TODO doc string"""
        stop_time = _now() + _timedelta(seconds=int(limit)) if limit else None

        if(register_address):
            self.register()

        while True:
            self.ping()
            if stop_time and _now() >= stop_time:
                return True
            time.sleep(int(delay))


def main(args):
    try:
        command_name, arguments = cli.parse_args(args)
        api = ClientApi(arguments.pop("address"), url=arguments.pop("url"))
        return getattr(api, command_name)(**arguments)
    except exceptions.DataservClientException as e:
        print("THIS FUCKING EXCEPTION")
        print(e)
        return None
