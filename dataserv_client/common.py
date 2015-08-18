import os


DEFAULT_URL = "http://status.driveshare.org"
DEFAULT_DELAY = 15

DEFAULT_APP_HOME = os.path.join(os.path.expanduser("~"), ".storj")


# build
SHARD_SIZE = 1024 * 1024 * 128  # 128 MB
DEFAULT_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB
DEFAULT_STORE_PATH = os.path.join(DEFAULT_APP_HOME, "store")


# connection retry
DEFAULT_CONNECTION_RETRY_LIMIT = 12  # 12 * 5 mins = 1 hour
DEFAULT_CONNECTION_RETRY_DELAY = 300   # 5 mins
