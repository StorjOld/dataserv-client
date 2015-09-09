#!/usr/bin/env python3
from future.standard_library import install_aliases
install_aliases()

from datetime import datetime
from datetime import timedelta
from btctxstore import BtcTxStore
from dataserv_client import control
from dataserv_client import common
from dataserv_client import builder
from dataserv_client import exceptions
from dataserv_client import messaging
from dataserv_client import deserialize
from dataserv_client import __version__

import os
import time

logger = common.logging.getLogger(__name__)


SHOW_CONFIG_TEMPLATE = """Current configuration.

    Authentication address: {0}
    Payout address: {1}
"""


# TODO move all logic to control, api should only deserialize/validate input


class Client(object):

    def __init__(self, url=common.DEFAULT_URL, debug=False, quiet=False,
                 use_folder_tree=False, max_size=common.DEFAULT_MAX_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 config_path=common.DEFAULT_CONFIG_PATH,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        debug = deserialize.flag(debug)
        quiet = deserialize.flag(quiet)

        self.url = deserialize.url(url)
        self.use_folder_tree = deserialize.flag(use_folder_tree)
        self.max_size = deserialize.byte_count(max_size)

        self.messenger = None  # lazy
        self.btctxstore = BtcTxStore()
        self.retry_limit = deserialize.positive_integer(connection_retry_limit)
        self.retry_delay = deserialize.positive_integer(connection_retry_delay)

        # paths
        self.cfg_path = os.path.realpath(config_path)
        control.util.ensure_path_exists(os.path.dirname(self.cfg_path))
        self.store_path = os.path.realpath(store_path)
        control.util.ensure_path_exists(self.store_path)

        # check for vfat partions
        fstype = control.util.get_fs_type(self.store_path)
        if fstype == "vfat":
            logger.info("Detected vfat partition, using folder tree.")
            self.use_folder_tree = True
        if fstype is None:
            msg = "Couldn't detected partition type for '{0}'"
            logger.warning(msg.format(self.store_path))

        self.cfg = control.config.get(self.btctxstore, self.cfg_path)

    @staticmethod
    def version():
        print(__version__)
        return __version__

    def _init_messenger(self):
        """Make sure messenger exists."""
        if self.messenger is None:
            wif = self.btctxstore.get_key(self.cfg["wallet"])
            self.messenger = messaging.Messaging(self.url, wif,
                                                 self.retry_limit,
                                                 self.retry_delay)

    def register(self):
        """Attempt to register the config address."""
        self._init_messenger()
        payout_address = self.cfg["payout_address"]
        self.messenger.register(payout_address)
        logger.info("Registered on server '{0}'.".format(self.url))
        return True

    def config(self, set_wallet=None, set_payout_address=None):
        """
        Set and then show the config settings.

        :param set_wallet: Set the HWIF for registration/auth address.
        :param set_payout_address:  Set the payout address.
        :return: Configuation object.
        """
        if((set_payout_address is not None) and
                (not self.btctxstore.validate_address(set_payout_address))):
            raise exceptions.InvalidAddress(set_payout_address)
        if((set_wallet is not None) and
                (not self.btctxstore.validate_wallet(set_wallet))):
            raise exceptions.InvalidHWIF(set_wallet)

        self._init_messenger()
        config_updated = False

        # update payout address if requested
        if set_payout_address:
            self.cfg["payout_address"] = set_payout_address
            config_updated = True

        # update wallet if requested
        if set_wallet:
            self.cfg["wallet"] = set_wallet
            config_updated = True

        # save config if updated
        if config_updated:
            control.config.save(self.btctxstore, self.cfg_path, self.cfg)

        # display config
        print(SHOW_CONFIG_TEMPLATE.format(
            self.messenger.auth_address(),
            self.cfg["payout_address"]
        ))
        return self.cfg

    def ping(self):
        """Attempt one keep-alive with the server."""
        self._init_messenger()

        msg = "Pinging server '{0}' at {1:%Y-%m-%d %H:%M:%S}."
        logger.info(msg.format(self.messenger.server_url(), datetime.now()))
        self.messenger.ping()

        return True

    def poll(self, delay=common.DEFAULT_DELAY, limit=None):
        """Attempt continuous keep-alive with the server.

        :param delay: Delay in seconds per ping of the server.
        :param limit: Number of seconds in the future to stop polling.
        :return: True, if limit is reached. None, if otherwise.
        """
        delay = deserialize.positive_integer(delay)
        stop_time = None
        if limit:
            stop_time = datetime.now() + timedelta(seconds=int(limit))

        while True:  # ping the server every X seconds
            self.ping()

            if stop_time and datetime.now() >= stop_time:
                return True
            time.sleep(int(delay))

    def build(self, cleanup=False, rebuild=False,
              set_height_interval=common.DEFAULT_SET_HEIGHT_INTERVAL):
        """Generate test files deterministically based on address.

        :param cleanup: Remove files in shard directory.
        :param rebuild: Re-generate any file shards.
        :param set_height_interval: Number of shards to generate before
                                    notifying the server.
        """
        set_height_interval = deserialize.positive_nonzero_integer(
            set_height_interval
        )
        cleanup = deserialize.flag(cleanup)
        rebuild = deserialize.flag(rebuild)

        self._init_messenger()
        logger.info("Starting build")

        def _on_generate_shard(cur_height, cur_seed, cur_file_hash):
            """
            Because URL requests are slow, only update the server when we are
            at the first height, at some height_interval, or the last height.

            :param cur_height: Current height in the building process.
            """
            first = cur_height == 1
            set_height = (cur_height % int(set_height_interval)) == 0
            last = int(self.max_size / common.SHARD_SIZE) == cur_height

            if first or set_height or last:
                self.messenger.height(cur_height)
                logger.info("Current height at {0}.".format(cur_height))

        # Initialize builder and generate/re-generate shards
        bldr = builder.Builder(self.cfg["payout_address"],
                               common.SHARD_SIZE, self.max_size,
                               on_generate_shard=_on_generate_shard,
                               use_folder_tree=self.use_folder_tree)
        generated = bldr.build(self.store_path, cleanup=cleanup,
                               rebuild=rebuild)

        logger.info("Build finished")
        return generated

    def farm(self):
        """ Fully automatic client for users wishing a simple turnkey solution.
        This will run all functions automatically with the most sane defaults
        and as little user interface as possible.
        """

        # farmer never gives up
        self._init_messenger()
        self.messenger.retry_limit = 99999999999999999999999999999999999999

        try:
            self.register()
        except exceptions.AddressAlreadyRegistered:
            pass  # already registered ...
        self.build()
        self.poll()
