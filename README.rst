===============
dataserv-client
===============

|BuildLink|_ |CoverageLink|_ |BuildLink2|_ |CoverageLink2|_ |LicenseLink|_

.. |BuildLink| image:: https://img.shields.io/travis/Storj/dataserv-client/master.svg?label=Build-Master
.. _BuildLink: https://travis-ci.org/Storj/dataserv-client

.. |CoverageLink| image:: https://img.shields.io/coveralls/Storj/dataserv-client/master.svg?label=Coverage-Master
.. _CoverageLink: https://coveralls.io/r/Storj/dataserv-client

.. |BuildLink2| image:: https://img.shields.io/travis/Storj/dataserv-client/develop.svg?label=Build-Develop
.. _BuildLink2: https://travis-ci.org/Storj/dataserv-client

.. |CoverageLink2| image:: https://img.shields.io/coveralls/Storj/dataserv-client/develop.svg?label=Coverage-Develop
.. _CoverageLink2: https://coveralls.io/r/Storj/dataserv-client

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/dataserv-client


Contributing
============

We welcome contributions if you have a little extra time and Python experience. We ask that you make your pull requests on the `develop <https://github.com/Storj/dataserv-client/tree/develop>`_ branch, as we only use `master <https://github.com/Storj/dataserv-client/tree/master>`_ for releases. Please follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, and make sure you document anything new. If you have any questions, you can find the entire team on `Slack <http://slack.storj.io/>`_. Note: If you plan on running the unit tests for the repo, you will also need to have `dataserv <https://github.com/Storj/dataserv>`_ running locally with a new db.


Setup
=====

Windows
-------

Download `latest windows release from github <https://github.com/Storj/dataserv-client/releases>`_.

Extract the zip file to the folder where you wish to have it installed.

::

    $ dataserv-client.exe version

The dataserv-client will automatically update when new releases are made.


Linux (Ubuntu/Mint/Debian)
--------------------------

Install client

::

    # install apt dependencies
    $ sudo apt-get install python python-pip python-dev gcc

    $ sudo pip install dataserv-client
    $ dataserv-client version

Update client

::

    $ sudo pip install dataserv-client --upgrade
    $ dataserv-client version


OSX
---

Install client

::

    $ brew install python graphviz
    $ rehash
    $ sudo pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"
    $ pip install dataserv-client
    $ dataserv-client version

Update client

::

    $ pip install dataserv-client --upgrade
    $ dataserv-client version


Farmer Quickstart Guide
=======================

**Configure your farmer node**

Optionally set a cold storage payout address.
You can set a counterparty wallet address here.
All configuration must be done before starting the node.

::

    dataserv-client config --set_payout_address=<BITCOIN_ADDRESS>



**Start your farmer node**

Optionally specify the path to store data, the available space, and minimum free space.

::

    dataserv-client --store_path=<PATH> --max_size=<SIZE_IN_BYTES> --min_free_size=<SIZE_IN_BYTES> farm

Optional max_size and min_free_size syntax

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

In order to farm on multiple discs you will have to run several instances,
as multiple paths are not yet supported. To do this you will need one config
for each disc.

Different instances can share a common payout address, however it is recommended
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


Farmer Setting Custom Height
============================


In order to build a bit faster, you may consider using the --set_height_interval command.
If you set a high height number though please also consider running another instance of the client with poll.
Poll will send every 60 sec, farm or build will send only when the height interval is reached.


Running the farm command
------------------------

::

    dataserv-client --url=http://status.driveshare.org --store_path=<PATH> --max_size=<SIZE_IN_BYTES> farm --set_height_interval=(default: 25, max recommended: 199999)


Running the poll command
------------------------

::

	dataserv-client --url=http://status.driveshare.org poll

Workers Guide
=============

You can start multiple workers by executing farm or build with the optional argument --workers. It is recommended to start only as many workers as your cpu and hard drive can handle. With a fast hard drive a cpu usage of ~80% is possible.

::

    dataserv-client build --workers=<number of workers>

::

    dataserv-client farm --workers=<number of workers>


Command Line Interface Usage
============================

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
      --min_free_size MIN_FREE_SIZE
                            Minimum free size in bytes. (default: 1073741824).
      --store_path STORE_PATH
                            Storage path. (default: /home/user/.storj/store).
      --config_path CONFIG_PATH
                            Config path. (default: /home/user/.storj/config.json).
      --debug               Show debug information.
      --quiet               Only show warning and error information.
      --use_folder_tree     Use folder tree to store files (always on for fat32
                            store_path).

    commands:
      <command>
        version             Show version number.
        register            Register your node on the network.
        ping                Ping master node.
        poll                Let the network know your are online.
        build               Fill the farmer with data up to their max.
        audit               Audit the generated data.
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

