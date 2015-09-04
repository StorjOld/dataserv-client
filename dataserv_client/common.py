import os
import logging


DEFAULT_URL = "http://status.driveshare.org"
DEFAULT_DELAY = 15

DEFAULT_APP_HOME = os.path.join(os.path.expanduser("~"), ".storj")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_APP_HOME, "config.json")


# build
DEFAULT_SET_HEIGHT_INTERVAL = 25
SHARD_SIZE = 1024 * 1024 * 128  # 128 MB
DEFAULT_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB
DEFAULT_STORE_PATH = os.path.join(DEFAULT_APP_HOME, "store")


# connection retry
DEFAULT_CONNECTION_RETRY_LIMIT = 120  # 120 * 30sec = 1 hour
DEFAULT_CONNECTION_RETRY_DELAY = 30


_log_format = "%(levelname)s %(name)s %(lineno)d: %(message)s"      
logging.basicConfig(format=_log_format, level=logging.DEBUG)
