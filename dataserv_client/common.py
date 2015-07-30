import os


DEFAULT_URL = "http://104.236.104.117"
DEFAULT_DELAY = 15

APP_HOME = os.path.join(os.path.expanduser("~"), ".storj")

# build
SHARD_SIZE = 1024 * 1024 * 128  # 128 MB
DEFAULT_MAX_SIZE = 1024 * 1024 * 1024  # 1 GB
DEFAULT_STORE_PATH = os.path.join(APP_HOME, "store")


