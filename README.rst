===============
dataserv-client
===============

|BuildLink|_ |CoverageLink|_ |LicenseLink|_ |IssuesLink|_


.. |BuildLink| image:: https://travis-ci.org/Storj/dataserv-client.svg?branch=master
.. _BuildLink: https://travis-ci.org/Storj/dataserv-client

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/dataserv-client/badge.svg
.. _CoverageLink: https://coveralls.io/r/Storj/dataserv-client

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/dataserv-client

.. |IssuesLink| image:: https://img.shields.io/github/issues/Storj/dataserv-client.svg
.. _IssuesLink: https://github.com/Storj/dataserv-client/issues


Setup
=====


Linux
-----

::

    $ sudo pip install dataserv-client
    $ dataserv-client version


Windows
-------

Download and install `Python 3.4 <https://www.python.org/downloads/release/python-343/>`_
TODO add pycrypto instructions

::

    $ pip install dataserv-client
    $ dataserv-client.py version


Command line interface usage
============================

Argument ordering
-----------------

::

    $ dataserv-client.py <program arguments> COMMAND <command arguments>


Argument ordering example
-------------------------

::

    $ dataserv-client.py --address=1Dnpy4qd5XSsiAgwX8EqYbR2DLV2kB1Kha --max_size=2147483648 build --cleanup


Show programm help, optional arguments and commands
---------------------------------------------------

::

    $ dataserv-client.py --help
    usage: dataserv-client.py [-h] [--address ADDRESS] [--url URL]
                              [--max_size MAX_SIZE] [--store_path STORE_PATH]
                              [--debug]
                              <command> ...

    Dataserve client command-line interface.

    optional arguments:
      -h, --help            show this help message and exit
      --address ADDRESS     Required bitcoin address.
      --url URL             Url of the farmer (default: http://104.236.104.117).
      --max_size MAX_SIZE   Maximum data size in bytes. (default: 1073741824).
      --store_path STORE_PATH
                            Storage path. (default: /home/storj/.storj/store).
      --debug               Show debug information.

    commands:
      <command>
        version             Print version number.
        register            Register a bitcoin address with farmer.
        ping                Ping farmer with given address.
        poll                Continuously ping farmer with given address.
        build               Fill the farmer with data up to their max.



Show command help and optional arguments
----------------------------------------

::

    $ dataserv-client.py <COMMAND> --help


version command
---------------

Show version number

::

    $ dataserv-client.py version


register command
----------------

Register address with default farmer.

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> register

Register address with custom farmer.

::

    $ dataserv-client.py --url=<CUSTOM_FARMER_URL> --address=<BITCOIN_ADDRESS> register


ping command
------------

Ping address:

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> ping


poll command
------------

Poll address:

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> poll


build command
-------------

Build

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build


Build with custom max data size and store path

::

    $ dataserv-client.py --store_path=<PATH_TO_FOLDER> --max_size=<MAX_DATA_SIZE_IN_BYTES> --address=<BITCOIN_ADDRESS> build


Build and cleanup files afterwards

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build --cleanup


Build custom shard height

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build --height=<NUMBER_OF_SHARDS>
