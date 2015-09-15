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


Contributing
============
-----------

We welcome contributions if you have a little extra time and Python experience. We ask that you make your pull requests on the `develop <https://github.com/Storj/dataserv-client/tree/develop>`_ branch, as we only use `master <https://github.com/Storj/dataserv-client/tree/master>`_ for releases. Please follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, and make sure you document anything new. If you have any questions, you can find the entire team on `Slack <http://slack.storj.io/>`_. Note: If you plan on running the unit tests for the repo, you will also need to have `dataserv <https://github.com/Storj/dataserv>`_ running locally.


Setup
=====
-----------

Windows
-------

Download `latest windows release from github <https://github.com/Storj/dataserv-client/releases>`_.

Extract the zip file to the folder where you wish to have it installed.

::

    $ dataserv-client.exe version

The dataserv-client will automatically update when new releases are made.


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


Farmer Quickstart Guide
=======================
-----------

**Configure your farmer node**

Optionally set a cold storage payout address.
You can set a counterparty wallet address here.
All configuration must be done before starting the node.

::

    dataserv-client config --set_payout_address=<BITCOIN_ADDRESS>



**Start your farmer node**

Optionally specify the path to store data path and available space.

::

    dataserv-client --store_path=<PATH> --max_size=<SIZE_IN_BYTES> farm

Optional max_size syntax

::

    --max_size=1.0K  # 1024^1 bytes
    --max_size=1.0KB # 1000^1 bytes
    --max_size=1.0M  # 1024^2 bytes
    --max_size=1.0MB # 1000^2 bytes
    --max_size=1.0G  # 1024^3 bytes
    --max_size=1.0GB # 1000^3 bytes
    --max_size=1.0T  # 1024^4 bytes
    --max_size=1.0TB # 1000^4 bytes
    --max_size=1.0P  # 1024^5 bytes
    --max_size=1.0PB # 1000^5 bytes


Farmer Multi Disc Guide
=======================
-----------

In order to farm on multiple discs you will have to run several instances,
as multiple paths are not yet supported. To do this you will need one config
for each disc.

Each instance can share a common payout address, however it is recommended
to use a different payout address for each instance.


Disc 1
------

::

    dataserv-client --config_path=<CONFIG 1> config --set_payout_address=<BITCOIN_ADDRESS 1>
    dataserv-client --config_path=<CONFIG 1> --store_path=<PATH 1> --max_size=<SIZE 1> farm


Disc n
------

::

    dataserv-client --config_path=<CONFIG n> config --set_payout_address=<BITCOIN_ADDRESS n>
    dataserv-client --config_path=<CONFIG n> --store_path=<PATH n> --max_size=<SIZE n> farm


Command Line Interface Usage
============================
-----------

Argument ordering
-----------------

::

    $ dataserv-client <program arguments> COMMAND <command arguments>


Argument ordering example
-------------------------

::

    $ dataserv-client --debug build --rebuild


Show program help, optional arguments and commands
--------------------------------------------------

::

    $ dataserv-client --help
    usage: dataserv-client [-h] [--url URL] [--max_size MAX_SIZE]
                           [--store_path STORE_PATH] [--config_path CONFIG_PATH]
                           [--debug] [--use_folder_tree]
                           <command> ...

    Dataserve client command-line interface.

    optional arguments:
      -h, --help            show this help message and exit
      --url URL             Url of the farmer (default:
                            http://status.driveshare.org).
      --max_size MAX_SIZE   Maximum data size in bytes. (default: 1073741824).
      --store_path STORE_PATH
                            Storage path. (default: /home/user/.storj/store).
      --config_path CONFIG_PATH
                            Config path. (default: /home/user/.storj/config.json).
      --debug               Show debug information.
      --use_folder_tree     Use folder tree to store files (always on for fat32
                            store_path).

    commands:
      <command>
        version             Show version number.
        register            Register your node on the network.
        ping                Ping master node.
        poll                Let the network know your are online.
        build               Fill the farmer with data up to their max.
        config              Edit and display config.
        farm                Start farmer.


Show command help and optional arguments
----------------------------------------

::

    $ dataserv-client config --help
    usage: dataserv-client config [-h] [--set_wallet SET_WALLET]
                                  [--set_payout_address SET_PAYOUT_ADDRESS]

    optional arguments:
      -h, --help            show this help message and exit
      --set_wallet SET_WALLET
                            Set node wallet to given hwif.
      --set_payout_address SET_PAYOUT_ADDRESS
                            Root address of wallet used by default.

