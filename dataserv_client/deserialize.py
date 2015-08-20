
def byte_count(byte_count): # ugly but much faster and safer then regex
    # FIXME handle parse errors

    # default value or python api used
    if isinstance(byte_count, int):
        return byte_count

    def _get_byte_count(postfix, base, exponant):
        char_num = len(postfix)
        if byte_count[-char_num:] == postfix:
            return int(byte_count[:-char_num]) * (base ** exponant)
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

    return int(byte_count)


