from __future__ import absolute_import, print_function


def format_list(l):
    return "[" + " ".join(map(lambda a: str.format("{0:02x}", a), l)) + "]"


