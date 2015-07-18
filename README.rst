###############
dataserv-client
###############

[![Build Status](https://travis-ci.org/Storj/dataserv-client.svg?branch=master)](https://travis-ci.org/Storj/dataserv-client)
[![Coverage Status](https://coveralls.io/repos/Storj/dataserv-client/badge.svg)](https://coveralls.io/r/Storj/dataserv-client)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/storj/dataserv-client/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/storj/dataserv-client.svg)](https://github.com/storj/dataserv-client/issues)


Setup
#####

1. Download and install [Python 3.4](https://www.python.org/downloads/release/python-343/)
2. Download the [client](https://github.com/Storj/dataserv-client/blob/master/client.py)
3. Run the script

Usage
#####

show programm help:

::

    $ ./client.py --help

show command help:

::

    $ ./client.py <COMMAND> --help

register address with default node:

::

    $ ./client.py register <YOUR_BITCOIN_ADDRESS>

register address with custom node:

::

    $ ./client.py register <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>

continuously ping default node in 15 sec intervals:

::

    $ ./client.py poll <YOUR_BITCOIN_ADDRESS>

continuously ping custom node in 15 sec intervals:

::

    $ ./client.py poll <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>
