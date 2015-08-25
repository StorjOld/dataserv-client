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


Quickstart example
------------------

::

    # Optional: Payout address and wallet are generated automatically.
    $ dataserv-client --set_payout_address=<BITCOIN_ADDRESS> show_config
    $ dataserv-client --set_wallet=<HWIF> show_config

    # register your node
    $ dataserv-client register

    # create shards
    $ dataserv-client build

    # let the network know you are online
    $ dataserv-client poll


Build with custom max data size and store path

::

    $ dataserv-client --store_path=<PATH_TO_FOLDER> --max_size=<MAX_DATA_SIZE_IN_BYTES> build

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


Argument ordering
-----------------

::

    $ dataserv-client <program arguments> COMMAND <command arguments>


Argument ordering example
-------------------------

::

    $ dataserv-client --max_size=10G build --rebuild


Show program help, optional arguments and commands
--------------------------------------------------

::

    $ dataserv-client --help
    usage: dataserv-client [-h] [--url URL] [--max_size MAX_SIZE]
                           [--store_path STORE_PATH] [--config_path CONFIG_PATH]
                           [--debug] [--set_wallet SET_WALLET]
                           [--set_payout_address SET_PAYOUT_ADDRESS]
                           <command> ...

    Dataserve client command-line interface.

    optional arguments:
      -h, --help            show this help message and exit
      --url URL             Url of the farmer (default:
                            http://status.driveshare.org).
      --max_size MAX_SIZE   Maximum data size in bytes. (default: 1073741824).
      --store_path STORE_PATH
                            Storage path. (default: /home/username/.storj/store).
      --config_path CONFIG_PATH
                            Config path. (default: /home/username/.storj/config.json).
      --debug               Show debug information.
      --set_wallet SET_WALLET
                            Set node wallet to given hwif.
      --set_payout_address SET_PAYOUT_ADDRESS
                            Root address of wallet used by default.

    commands:
      <command>
        version             Show version number.
        register            Register your node on the network.
        ping                Ping master node.
        poll                Let the network know your are online.
        build               Fill the farmer with data up to their max.
        show_config         Display saved config.



Show command help and optional arguments
----------------------------------------

::

    $ dataserv-client build --help
    usage: dataserv-client build [-h] [--cleanup] [--rebuild]
                                 [--set_height_interval SET_HEIGHT_INTERVAL]

    optional arguments:
      -h, --help            show this help message and exit
      --cleanup             Remove generated files.
      --rebuild             Replace previously files.
      --set_height_interval SET_HEIGHT_INTERVAL
                            Interval at which to set height (default: 25).

