#!/usr/bin/env python3
import os
import hashlib
import time
import psutil
import storjnode
from datetime import datetime
from datetime import timedelta
from btctxstore import BtcTxStore
from dataserv_client import common
from dataserv_client import builder
from dataserv_client import exceptions
from dataserv_client import messaging
from dataserv_client import deserialize
from dataserv_client import __version__
from crochet import setup
setup()  # start twisted via crochet


logger = common.logging.getLogger(__name__)


SHOW_CONFIG_TEMPLATE = """Current configuration.

    Authentication address: {0}
    Payout address: {1}
"""


# TODO move all logic to control, api should only deserialize/validate input


class Client(object):

    def __init__(self, url=common.DEFAULT_URL, debug=False, quiet=False,
                 use_folder_tree=False, max_size=common.DEFAULT_MAX_SIZE,
                 min_free_size=common.DEFAULT_MIN_FREE_SIZE,
                 store_path=common.DEFAULT_STORE_PATH,
                 config_path=common.DEFAULT_CONFIG_PATH,
                 connection_retry_limit=common.DEFAULT_CONNECTION_RETRY_LIMIT,
                 connection_retry_delay=common.DEFAULT_CONNECTION_RETRY_DELAY):

        debug = deserialize.flag(debug)
        quiet = deserialize.flag(quiet)

        self.url = deserialize.url(url)
        self.use_folder_tree = deserialize.flag(use_folder_tree)
        self.max_size = deserialize.byte_count(max_size)
        self.min_free_size = deserialize.byte_count(min_free_size)

        self.messenger = None  # lazy
        self.btctxstore = BtcTxStore()
        self.retry_limit = deserialize.positive_integer(connection_retry_limit)
        self.retry_delay = deserialize.positive_integer(connection_retry_delay)

        # paths
        self.cfg_path = os.path.realpath(config_path)
        storjnode.util.ensure_path_exists(os.path.dirname(self.cfg_path))
        self.store_path = os.path.realpath(store_path)
        storjnode.util.ensure_path_exists(self.store_path)

        # check for vfat partions
        try:
            fstype = storjnode.util.get_fs_type(self.store_path)

        # FileNotFoundError: [Errno 2] No such file or directory: '/etc/mtab'
        # psutil: https://code.google.com/p/psutil/issues/detail?id=434
        except EnvironmentError as e:
            logger.warning(e)
            fstype = None

        if fstype == "vfat":
            logger.info("Detected vfat partition, using folder tree.")
            self.use_folder_tree = True
        if fstype is None:
            msg = "Couldn't detected partition type for '{0}'"
            logger.warning(msg.format(self.store_path))

        self.cfg = storjnode.config.get(self.btctxstore, self.cfg_path)

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
            storjnode.config.save(self.btctxstore, self.cfg_path, self.cfg)

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
        if limit is not None:
            stop_time = datetime.now() + timedelta(seconds=int(limit))

        while True:  # ping the server every X seconds
            self.ping()

            if stop_time and datetime.now() >= stop_time:
                return True
            time.sleep(int(delay))

    def freespace(self):
        freespace = psutil.disk_usage(self.store_path).free
        print(freespace)
        return freespace

    def build(self, workers=1, cleanup=False, rebuild=False, repair=False,
              set_height_interval=common.DEFAULT_SET_HEIGHT_INTERVAL):
        """Generate test files deterministically based on address.

        :param workers: Number of Number of threadpool workers.
        :param cleanup: Remove files in shard directory.
        :param rebuild: Re-generate any file shards.
        :param set_height_interval: Number of shards to generate before
                                    notifying the server.
        """

        workers = deserialize.positive_nonzero_integer(workers)

        set_height_interval = deserialize.positive_nonzero_integer(
            set_height_interval
        )
        cleanup = deserialize.flag(cleanup)
        rebuild = deserialize.flag(rebuild)
        repair = deserialize.flag(repair)

        self._init_messenger()
        logger.info("Starting build")

        def _on_generate_shard(cur_height, last):
            """
            Because URL requests are slow, only update the server when we are
            at the first height, at some height_interval, or the last height.

            :param cur_height: Current height in the building process.
            """
            first = cur_height == 1
            set_height = (cur_height % int(set_height_interval)) == 0

            if first or set_height or last:
                self.messenger.height(cur_height)
                logger.info("Current height at {0}.".format(cur_height))

        # Initialize builder and generate/re-generate shards
        bldr = builder.Builder(address=self.cfg["payout_address"],
                               shard_size=common.SHARD_SIZE,
                               max_size=self.max_size,
                               min_free_size=self.min_free_size,
                               on_generate_shard=_on_generate_shard,
                               use_folder_tree=self.use_folder_tree)
        generated = bldr.build(self.store_path, workers=workers,
                               cleanup=cleanup, rebuild=rebuild, repair=repair)

        logger.info("Build finished")
        return generated

    def audit(self, delay=common.DEFAULT_AUDIT_DELAY, limit=None):

        self._init_messenger()

        # Initialize builder and audit shards
        bldr = builder.Builder(address=self.cfg["payout_address"],
                               shard_size=common.SHARD_SIZE,
                               max_size=self.max_size,
                               min_free_size=self.min_free_size,
                               use_folder_tree=self.use_folder_tree)

        delay = deserialize.positive_integer(delay)
        stop_time = None
        if limit is not None:
            stop_time = datetime.now() + timedelta(seconds=int(limit))

        btc_index = 0
        while True:
            btc_block = bldr.btc_last_confirmed_block(
                min_confirmations=common.DEFAULT_MIN_CONFIRMATIONS
            )
            if btc_block['block_no'] != btc_index:
                btc_hash = btc_block['blockhash']
                btc_index = btc_block['block_no']

                logger.debug("Using bitcoin block {0} hash {1}.".format(
                    btc_index, btc_hash))

                wif = self.btctxstore.get_key(self.cfg["wallet"])
                address = self.btctxstore.get_address(wif)
                response_data = address + btc_hash + str(bldr.audit(
                                                        self.store_path,
                                                        btc_block['block_no'],
                                                        btc_block['blockhash']))
                response = hashlib.sha256(
                    response_data.encode('utf-8')
                ).hexdigest()

                # New Dataserv Server version is needed
                self.messenger.audit(btc_block['block_no'], response)
            else:
                msg = "Bitcoin block {0} already used. Waiting for new block."
                logger.debug(msg.format(btc_index))

            if stop_time and datetime.now() >= stop_time:
                return True
            time.sleep(int(delay))

    def farm(self, workers=1, cleanup=False, rebuild=False, repair=False,
             set_height_interval=common.DEFAULT_SET_HEIGHT_INTERVAL,
             delay=common.DEFAULT_DELAY, limit=None):
        """ Fully automatic client for users wishing a simple turnkey solution.
        This will run all functions automatically with the most sane defaults
        and as little user interface as possible.

        :param workers: Number of Number of threadpool workers.
        :param cleanup: Remove files in shard directory.
        :param rebuild: Re-generate any file shards.
        :param set_height_interval: Number of shards to generate before
                                    notifying the server.
        :param delay: Delay in seconds per ping of the server.
        :param limit: Number of seconds in the future to stop polling.
        """

        workers = deserialize.positive_nonzero_integer(workers)

        set_height_interval = deserialize.positive_nonzero_integer(
            set_height_interval
        )
        cleanup = deserialize.flag(cleanup)
        rebuild = deserialize.flag(rebuild)
        repair = deserialize.flag(repair)

        # farmer never gives up
        self._init_messenger()
        self.messenger.retry_limit = 99999999999999999999999999999999999999

        try:
            self.register()
        except exceptions.AddressAlreadyRegistered:
            pass  # already registered ...
        self.build(workers=workers, cleanup=cleanup, rebuild=rebuild,
                   repair=repair, set_height_interval=set_height_interval)
        self.poll(delay=delay, limit=limit)
        return True
