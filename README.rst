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
.. _IssuesLink: https://github.com/Storj/dataserv-client/issues


Linux Setup
###########

::

    $ pip install dataserv-client
    $ dataserv-client version


Windows Setup
#############

Download and install `Python 3.4 <https://www.python.org/downloads/release/python-343/>`_
TODO add pycrypto instructions

::

    $ pip install dataserv-client
    $ dataserv-client.py version


Usage
#####

Show programm help and optional arguments:

::

    $ dataserv-client.py --help


Show command help and optional arguments:

::

    $ dataserv-client.py <COMMAND> --help


Show version number

::

    $ dataserv-client.py version


Register address:

::

    $ dataserv-client.py --address=<YOUR_BITCOIN_ADDRESS> register


Ping address:

::

    $ dataserv-client.py --address=<YOUR_BITCOIN_ADDRESS> ping


Poll address:

::

    $ dataserv-client.py --address=<YOUR_BITCOIN_ADDRESS> poll


Build:

::

    $ dataserv-client.py --address=<YOUR_BITCOIN_ADDRESS> build
