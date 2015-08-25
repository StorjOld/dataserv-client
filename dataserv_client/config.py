import os
import json
import btctxstore
from dataserv_client import exceptions
from dataserv_client import __version__


def read(path, password=None):
    if password is None:  # unencrypted
        with open(path, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        raise Exception("encryption not implemented")


def save(btctxstore, path, config, password=None):
    # FIXME confirm overwrite previous config
    validate(btctxstore, config)
    if password is None:  # unencrypted
        with open(path, 'w') as config_file:
            config_file.write(json.dumps(config))
            return config
    else:
        raise Exception("encryption not implemented")


def create(btctxstore, path, password=None):
    hwif = btctxstore.create_wallet()
    wif = btctxstore.get_key(hwif)
    address = btctxstore.get_address(wif)
    config = {
        "version": __version__,
        "wallet": hwif,
        "payout_address": address,  # default to wallet address
    }
    return save(btctxstore, path, config, password=password)


def validate(btctxstore, config):

    # is a dict
    if not isinstance(config, dict):
        exceptions.InvalidConfig()

    # correct version
    if config.get("version") != __version__:
        exceptions.InvalidConfig()

    # has valid payout address
    if not btctxstore.validate_address(config.get("payout_address")):
        exceptions.InvalidConfig()

    # has valid wallet
    wif = btctxstore.get_key(config.get("wallet"))
    if not btctxstore.validate_key(wif):
        exceptions.InvalidConfig()


def get(btctxstore, path, password=None):
    if os.path.exists(path):
        config = read(path, password=password)
        # TODO migrate here
        validate(btctxstore, config)
        return config
    return create(btctxstore, path, password=password)
