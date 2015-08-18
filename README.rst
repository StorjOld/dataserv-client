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


Windows
-------

Download `latest windows release from github <https://github.com/Storj/dataserv-client/releases>`_. 

Extarct the zip file to the folder where you wish to have it installed.

::

    $ dataserv-client.exe version

The dataserv-client will automaticlly update when new releases are made.


Ubuntu Linux
------------

Install client

::

    $ sudo apt-get install python3-pip
    $ sudo pip3 install dataserv-client
    $ dataserv-client version

Update client

::

    $ sudo pip3 install dataserv-client --upgrade
    $ dataserv-client version


OSX
---

Install client

::

    $ brew install python3
    $ rehash 
    $ pip3 install dataserv-client
    $ dataserv-client version

Update client

::

    $ pip3 install dataserv-client --upgrade
    $ dataserv-client version


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


Show program help, optional arguments and commands
--------------------------------------------------

::

    $ dataserv-client.py --help
    usage: dataserv-client.py [-h] [--address ADDRESS] [--url URL]
                              [--max_size MAX_SIZE] [--store_path STORE_PATH]
                              [--debug]
                              <command> ...

    Dataserv client command-line interface.

    optional arguments:
      -h, --help            Show this help message and exit
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

    # optional max_size syntax
    --max_size=1K  # 1024^1 bytes
    --max_size=1KB # 1000^1 bytes
    --max_size=1M  # 1024^2 bytes
    --max_size=1MB # 1000^2 bytes
    --max_size=1G  # 1024^3 bytes
    --max_size=1GB # 1000^3 bytes
    --max_size=1T  # 1024^4 bytes
    --max_size=1TB # 1000^4 bytes
    --max_size=1P  # 1024^5 bytes
    --max_size=1PB # 1000^5 bytes


Build and cleanup files afterwards

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build --cleanup


Build and force rebuild of any previously generated files.

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build --rebuild


Build custom shard height

::

    $ dataserv-client.py --address=<BITCOIN_ADDRESS> build --height=<NUMBER_OF_SHARDS>
