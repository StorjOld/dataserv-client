import sys
import argparse
from dataserv_client import common
from dataserv_client import api


def _add_programm_args(parser):
    # address
    parser.add_argument("address", help="Required bitcoin address.")

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

    # debug
    parser.add_argument('--debug', action='store_true',
                        help="Show debug information.")


def _add_version(command_parser):
    version_parser = command_parser.add_parser(  # NOQA
        "version", help="Print version number."
    )

def _add_register(command_parser):
    register_parser = command_parser.add_parser(  # NOQA
        "register", help="Register a bitcoin address with farmer."
    )


def _add_ping(command_parser):
    ping_parser = command_parser.add_parser(  # NOQA
        "ping", help="Ping farmer with given address."
    )


def _add_poll(command_parser):
    poll_parser = command_parser.add_parser(
        "poll", help="Continuously ping farmer with given address."
    )
    poll_parser.add_argument(
        "--delay", default=common.DEFAULT_DELAY,
        help="Deley between each ping."
    )
    poll_parser.add_argument(
        "--limit", default=None, help="Limit poll time in seconds."
    )
    poll_parser.add_argument(
        '--register_address', action='store_true',
        help="Register address before polling."
    )


def _add_build(command_parser):
    build_parser = command_parser.add_parser(
        "build", help="Fill the farmer with data up to their max."
    )

    # cleanup
    build_parser.add_argument('--cleanup', action='store_true',
                              help="Remove generated files.")


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

    # get values
    arguments = vars(parser.parse_args(args=args))
    command_name = arguments.pop("command")
    if not command_name:
        parser.error("No command given!")
    return command_name, arguments


def main(args):
    command_name, arguments = _parse_args(args)
    client = api.Client(
        arguments.pop("address"),
        url=arguments.pop("url"),
        debug=arguments.pop("debug"),
        max_size=arguments.pop("max_size"),
        store_path=arguments.pop("store_path"),
    )
    return getattr(client, command_name)(**arguments)
