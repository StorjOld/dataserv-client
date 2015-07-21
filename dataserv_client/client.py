#!/usr/bin/env python3


import sys
import time
import urllib
import urllib.error
import urllib.request
import argparse


DEFAULT_URL = "http://104.236.104.117"
DEFAULT_DELAY = 15


class DataservClientException(Exception):
    pass


class AddressAlreadyRegistered(DataservClientException):

    def __init__(self, address, url):
        msg = "Address {0} already registered at {1}!".format(address, url)
        super(AddressAlreadyRegistered, self).__init__(msg)


class FarmerNotFound(DataservClientException):

    def __init__(self, url):
        msg = "Farmer not found at {0}!".format(url)
        super(FarmerNotFound, self).__init__(msg)


class FarmerError(DataservClientException):

    def __init__(self, url):
        msg = "Farmer error at {0}!".format(url)
        super(FarmerError, self).__init__(msg)


class InvalidAddress(DataservClientException):

    def __init__(self, address):
        msg = "Address {0} not valid!".format(address)
        super(InvalidAddress, self).__init__(msg)


class ConnectionError(DataservClientException):

    def __init__(self, url):
        msg = "Could not connect to server {0}!".format(url)
        super(ConnectionError, self).__init__(msg)


def register(address, url=DEFAULT_URL):
    """Attempt to register the config address."""

    try:
        api_call = "{0}/api/register/{1}".format(url, address)
        response = urllib.request.urlopen(api_call)
        if response.code == 200:
            print("Address {0} now registered on {1}.".format(address, url))
            return True

    except urllib.error.HTTPError as e:
        if e.code == 409:
            raise AddressAlreadyRegistered(address, url)
        elif e.code == 404:
            raise FarmerNotFound(url)
        elif e.code == 400:
            raise InvalidAddress(address)
        elif e.code == 500:
            raise FarmerError(url)
        else:
            raise e
    except urllib.error.URLError:
        raise ConnectionError(url)


def ping(address, url=DEFAULT_URL):
    """Attempt keep-alive with the server."""
    try:
        api_call = "{0}/api/ping/{1}".format(url, address)
        urllib.request.urlopen(api_call)
        print("Pinging {0} with address {1}.".format(url, address))
        return True

    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise InvalidAddress(address)
        elif e.code == 404:
            raise FarmerNotFound(url)
        elif e.code == 500:
            raise FarmerError(url)
        else:
            raise e
    except urllib.error.URLError:
        raise ConnectionError(url)


def poll(address, register=False, url=DEFAULT_URL, delay=DEFAULT_DELAY):
    if(register):
        register(address)
    while ping(address):
        time.sleep(delay)


def _parse_args():
    class ArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    # setup parser
    description = "Dataserve client command-line interface."
    parser = ArgumentParser(description=description)
    command_parser = parser.add_subparsers(
        title='commands', dest='command', metavar="<command>"
    )

    # register command
    register_parser = command_parser.add_parser(
        "register",
        help="Register a bitcoin address with farmer."
    )
    register_parser.add_argument(
        "address",
        help="Required bitcoin address."
    )
    register_parser.add_argument(
        "--url", default=DEFAULT_URL,
        help="Url of the farmer (default: {0}).".format(DEFAULT_URL)
    )

    # ping command
    ping_parser = command_parser.add_parser(
        "ping",
        help="Ping farmer with given address."
    )
    ping_parser.add_argument(
        "address",
        help="Required bitcoin address."
    )
    ping_parser.add_argument(
        "--url", default=DEFAULT_URL,
        help="Url of the farmer (default: {0}).".format(DEFAULT_URL)
    )

    # poll command
    poll_parser = command_parser.add_parser(
        "poll",
        help="Continuously ping farmer with given address."
    )
    poll_parser.add_argument(
        "address",
        help="Required bitcoin address."
    )
    poll_parser.add_argument(
        "--url", default=DEFAULT_URL,
        help="Url of the farmer (default: {0}).".format(DEFAULT_URL)
    )
    poll_parser.add_argument(
        "--delay", default=DEFAULT_DELAY,
        help="Deley between each ping."
    )
    poll_parser.add_argument(
        '--register', action='store_true',
        help="Register address before polling."
    )

    # get values
    arguments = vars(parser.parse_args())
    command_name = arguments.pop("command")
    if not command_name:
        parser.error("No command given!")
    return command_name, arguments


if __name__ == "__main__":
    command_name, arguments = _parse_args()
    commands = {
        "register": register,
        "ping": ping,
        "poll": poll
    }
    try:
        commands[command_name](**arguments)
    except DataservClientException as e:
        print(e)
