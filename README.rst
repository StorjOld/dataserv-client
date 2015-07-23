###############
dataserv-client
###############

|BuildLink|_ |CoverageLink|_ |LicenseLink|_ |IssuesLink|_


.. |BuildLink| image:: https://travis-ci.org/Storj/dataserv-client.svg?branch=master
.. _BuildLink: https://travis-ci.org/Storj/dataserv-client

.. |CoverageLink| image:: https://coveralls.io/repos/Storj/dataserv-client/badge.svg
.. _CoverageLink: https://coveralls.io/r/Storj/dataserv-client

.. |LicenseLink| image:: https://img.shields.io/badge/license-MIT-blue.svg
.. _LicenseLink: https://raw.githubusercontent.com/Storj/dataserv-client

.. |IssuesLink| image:: https://img.shields.io/github/issues/Storj/dataserv-client.svg
.. _IssuesLink: https://github.com/Storj/dataserv-client


Setup
#####

1. Download and install `Python 3.4 <https://www.python.org/downloads/release/python-343/>`_ 
2. Download the `client <https://github.com/Storj/dataserv-client/blob/master/client.py>`_ 
3. Run the script

Usage
#####

Show programm help:

::

    $ ./client.py --help

Show command help:

::

    $ ./client.py <COMMAND> --help

Register address with default node:

::

    $ ./client.py register <YOUR_BITCOIN_ADDRESS>

Register address with custom node:

::

    $ ./client.py register <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>

Continuously ping default node in 15 sec intervals:

::

    $ ./client.py poll <YOUR_BITCOIN_ADDRESS>

Continuously ping custom node in 15 sec intervals:

::

    $ ./client.py poll <YOUR_BITCOIN_ADDRESS> --url=<FARMER_URL>
