import os
import json
from dataserv_client import exceptions
from dataserv_client import __version__


def read(path, password=None):
    if password is None:  # unencrypted
        with open(path, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        raise Exception("encryption not implemented")


def save(btctxstore, path, cfg, password=None):
    validate(btctxstore, cfg)
    if password is None:  # unencrypted
        with open(path, 'w') as config_file:
            config_file.write(json.dumps(cfg))
            return cfg
    else:
        raise Exception("encryption not implemented")


def create(btctxstore, path, password=None):
    hwif = btctxstore.create_wallet()
    wif = btctxstore.get_key(hwif)
    address = btctxstore.get_address(wif)
    cfg = {
        "version": __version__,
        "wallet": hwif,
        "payout_address": address,  # default to wallet address
    }
    return save(btctxstore, path, cfg, password=password)


def validate(btctxstore, cfg):

    # is a dict
    if not isinstance(cfg, dict):
        raise exceptions.InvalidConfig()

    # correct version
    if cfg.get("version") != __version__:
        raise exceptions.InvalidConfig()

    # has valid payout address
    if not btctxstore.validate_address(cfg.get("payout_address")):
        raise exceptions.InvalidConfig()

    # has valid wallet
    if not btctxstore.validate_wallet(cfg.get("wallet")):
        raise exceptions.InvalidConfig()
    return True


def get(btctxstore, path, password=None):
    if os.path.exists(path):
        cfg = read(path, password=password)
        cfg = migrate(btctxstore, path, cfg, password=password)
        validate(btctxstore, cfg)
        return cfg
    return create(btctxstore, path, password=password)


def _set_version(btctxstore, cfg, new_version):
    cfg['version'] = new_version
    return cfg


def _migrate_200_to_201(btctxstore, cfg):
    _set_version(btctxstore, cfg, '2.0.1')

    # master_secret -> wallet
    master_secret = cfg['master_secret']
    if master_secret is None:
        raise exceptions.InvalidConfig()
    cfg['wallet'] = btctxstore.create_wallet(master_secret=master_secret)

    return cfg


_MIGRATIONS = {
    "2.0.0": _migrate_200_to_201,
    "2.0.1": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.0.2'),
    "2.0.2": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.0.3'),
    "2.0.3": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.1.0'),
    "2.1.0": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.1.1'),
    "2.1.1": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.1.2'),
    "2.1.2": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.1.3'),
    "2.1.3": lambda btctxstore, cfg: _set_version(btctxstore, cfg, '2.1.4'),
    # TODO add smarter version ranges so no new line needed for every version
}


def migrate(btctxstore, path, cfg, password=None):
    if not isinstance(cfg, dict) or 'version' not in cfg:
        raise exceptions.InvalidConfig()
    saved_version = cfg['version']

    # migrate until we are at current version
    while cfg['version'] != __version__:
        cfg = _MIGRATIONS[cfg['version']](btctxstore, cfg)

    # save if migrations were made
    if saved_version != cfg['version']:
        cfg = save(btctxstore, path, cfg, password=password)

    return cfg
