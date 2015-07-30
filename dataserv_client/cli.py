import sys
import argparse
from dataserv_client import common


def _add_programm_args(parser):
    parser.add_argument("address", help="Required bitcoin address.")
    parser.add_argument(
        "--url", default=common.DEFAULT_URL,
        help="Url of the farmer (default: {0}).".format(common.DEFAULT_URL)
    )


def _add_register(command_parser):
    register_parser = command_parser.add_parser(
        "register", help="Register a bitcoin address with farmer."
    )


def _add_ping(command_parser):
    ping_parser = command_parser.add_parser(
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


def parse_args(args):
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

    _add_register(command_parser)
    _add_ping(command_parser)
    _add_poll(command_parser)

    # get values
    arguments = vars(parser.parse_args(args=args))
    command_name = arguments.pop("command")
    if not command_name:
        parser.error("No command given!")
    return command_name, arguments


