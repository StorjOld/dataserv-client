from btctxstore.deserialize import *  # NOQA

import re
import decimal
from dataserv_client import exceptions


def positive_nonzero_integer(i):
    i = positive_integer(i)
    if i == 0:
        raise exceptions.InvalidInput("Value must be greater then 0!")
    return i


def url(urlstr):
    # source http://stackoverflow.com/a/7160778/90351
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    if not bool(regex.match(urlstr)):
        raise exceptions.InvalidUrl()
    return urlstr


def byte_count(byte_count):  # ugly but much faster and safer then regex

    # default value or python api used
    if isinstance(byte_count, int):
        return positive_nonzero_integer(byte_count)

    byte_count = unicode_str(byte_count)

    def _get_byte_count(postfix, base, exponant):
        char_num = len(postfix)
        if byte_count[-char_num:] == postfix:
            count = decimal.Decimal(byte_count[:-char_num])  # remove postfix
            return positive_nonzero_integer(count * (base ** exponant))
        return None

    # check base 1024
    if len(byte_count) > 1:
        n = None
        n = n if n is not None else _get_byte_count('K', 1024, 1)
        n = n if n is not None else _get_byte_count('M', 1024, 2)
        n = n if n is not None else _get_byte_count('G', 1024, 3)
        n = n if n is not None else _get_byte_count('T', 1024, 4)
        n = n if n is not None else _get_byte_count('P', 1024, 5)
        if n is not None:
            return n

    # check base 1000
    if len(byte_count) > 2:
        n = None
        n = n if n is not None else _get_byte_count('KB', 1000, 1)
        n = n if n is not None else _get_byte_count('MB', 1000, 2)
        n = n if n is not None else _get_byte_count('GB', 1000, 3)
        n = n if n is not None else _get_byte_count('TB', 1000, 4)
        n = n if n is not None else _get_byte_count('PB', 1000, 5)
        if n is not None:
            return n

    return positive_nonzero_integer(byte_count)


