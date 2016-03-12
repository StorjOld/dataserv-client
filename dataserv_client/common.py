import os
import binascii
from storjnode.log import logging  # NOQA
from pycoin.encoding import b2a_hashed_base58
from pycoin.encoding import a2b_hashed_base58


DEFAULT_URL = "http://status.driveshare.org"


# read default delay from os environ if available
if os.environ.get("DATASERV_MAX_PING"):
    DEFAULT_DELAY = os.environ.get("DATASERV_MAX_PING")
else:
    DEFAULT_DELAY = 60  # default seconds


DEFAULT_APP_HOME = os.path.join(os.path.expanduser("~"), ".storj")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_APP_HOME, "config.json")


# build
DEFAULT_SET_HEIGHT_INTERVAL = 25
SHARD_SIZE = 1024 * 1024 * 128  # 128 MB
DEFAULT_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB
DEFAULT_MIN_FREE_SIZE = 1024 * 1024 * 1024  # 1GB
DEFAULT_STORE_PATH = os.path.join(DEFAULT_APP_HOME, "store")

# audit
DEFAULT_MIN_CONFIRMATIONS = 6
DEFAULT_BLOCK_SIZE = 80
DEFAULT_AUDIT_DELAY = 60
DEFAULT_FULL_AUDIT = 1000


# connection retry
DEFAULT_CONNECTION_RETRY_LIMIT = 120  # 120 * 30sec = 1 hour
_retry_delay_label = "DATASERV_CLIENT_CONNECTION_RETRY_DELAY"
if os.environ.get(_retry_delay_label):
    DEFAULT_CONNECTION_RETRY_DELAY = int(os.environ.get(_retry_delay_label))
else:
    DEFAULT_CONNECTION_RETRY_DELAY = 30


def nodeid2address(hexnodeid):
    """Convert a node id to a bitcoin address."""
    nodeid = binascii.unhexlify(hexnodeid)
    return b2a_hashed_base58(b'\0' + nodeid)


def address2nodeid(address):
    """Convert a bitcoin address to a node id."""
    return binascii.hexlify(a2b_hashed_base58(address)[1:]).decode("utf-8")
