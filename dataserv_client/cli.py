import sys
import argparse
from dataserv_client import api
from dataserv_client import common


def _add_programm_args(parser):
    # url
    parser.add_argument(
        "--url", default=common.DEFAULT_URL,
        help="Url of the farmer (default: {0}).".format(common.DEFAULT_URL)
    )

    # max_size
    default = common.DEFAULT_MAX_SIZE
    parser.add_argument(
        "--max_size", default=default,
        help="Maximum data size in bytes. (default: {0}).".format(default)
    )

    # store_path
    default = common.DEFAULT_STORE_PATH
    parser.add_argument(
        "--store_path", default=default,
        help="Storage path. (default: {0}).".format(default)
    )

    # config_path
    default = common.DEFAULT_CONFIG_PATH
    parser.add_argument(
        "--config_path", default=default,
        help="Config path. (default: {0}).".format(default)
    )

    # debug
    parser.add_argument('--debug', action='store_true',
                        help="Show debug information.")

    # debug
    parser.add_argument('--quiet', action='store_true',
                        help="Only show warning and error information.")

    # use folder tree
    parser.add_argument(
        '--use_folder_tree', action='store_true',
        help="Use folder tree to store files (always on for fat32 store_path)."
    )


def _add_version(command_parser):
    version_parser = command_parser.add_parser(  # NOQA
        "version", help="Show version number."
    )


def _add_register(command_parser):
    register_parser = command_parser.add_parser(  # NOQA
        "register", help="Register your node on the network."
    )


def _add_ping(command_parser):
    ping_parser = command_parser.add_parser(  # NOQA
        "ping", help="Ping master node."
    )


def _add_config(command_parser):
    config_parser = command_parser.add_parser(  # NOQA
        "config", help="Edit and display config."
    )

    # wallet
    msg = "Set node wallet to given hwif."
    config_parser.add_argument("--set_wallet", default=None, help=msg)

    # payout_address
    msg = "Root address of wallet used by default."
    config_parser.add_argument("--set_payout_address", default=None, help=msg)


def _add_poll(command_parser):
    poll_parser = command_parser.add_parser(
        "poll", help="Let the network know your are online."
    )
    poll_parser.add_argument(
        "--delay", default=common.DEFAULT_DELAY,
        help="Deley between each ping."
    )
    poll_parser.add_argument(
        "--limit", default=None, help="Limit poll time in seconds."
    )


def _add_build(command_parser):
    build_parser = command_parser.add_parser(
        "build", help="Fill the farmer with data up to their max."
    )

    # cleanup
    build_parser.add_argument('--cleanup', action='store_true',
                              help="Remove generated files.")

    # rebuild
    build_parser.add_argument('--rebuild', action='store_true',
                              help="Replace previously files.")

    # set height interval
    default = common.DEFAULT_SET_HEIGHT_INTERVAL
    build_parser.add_argument(
        "--set_height_interval", default=default,
        help="Interval at which to set height (default: {0}).".format(default)
    )


def _add_farm(command_parser):
    farm_parser = command_parser.add_parser(
        "farm", help="Start farmer."
    )
    # cleanup
    farm_parser.add_argument('--cleanup', action='store_true',
                             help="Remove generated files.")

    # rebuild
    farm_parser.add_argument('--rebuild', action='store_true',
                             help="Replace previously files.")

    # set height interval
    default = common.DEFAULT_SET_HEIGHT_INTERVAL
    farm_parser.add_argument(
        "--set_height_interval", default=default,
        help="Interval at which to set height (default: {0}).".format(default)
    )

    farm_parser.add_argument(
        "--delay", default=common.DEFAULT_DELAY,
        help="Deley between each ping."
    )

    farm_parser.add_argument(
        "--limit", default=None, help="Limit poll time in seconds."
    )


def _parse_args(args):
    class ArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)
    # TODO let user put in store path and max size shard size is 128

    # setup parser
    description = "Dataserve client command-line interface."
    parser = ArgumentParser(description=description)

    _add_programm_args(parser)

    command_parser = parser.add_subparsers(
        title='commands', dest='command', metavar="<command>"
    )

    _add_version(command_parser)
    _add_register(command_parser)
    _add_ping(command_parser)
    _add_poll(command_parser)
    _add_build(command_parser)
    _add_config(command_parser)
    _add_farm(command_parser)

    # get values
    arguments = vars(parser.parse_args(args=args))
    command_name = arguments.pop("command")
    if not command_name:
        parser.error("No command given!")
    return command_name, arguments


def main(args):
    command_name, arguments = _parse_args(args)
    client = api.Client(
        url=arguments.pop("url"),
        debug=arguments.pop("debug"),
        quiet=arguments.pop("quiet"),
        use_folder_tree=arguments.pop("use_folder_tree"),
        max_size=arguments.pop("max_size"),
        store_path=arguments.pop("store_path"),
        config_path=arguments.pop("config_path"),
    )
    return getattr(client, command_name)(**arguments)
