from __future__ import absolute_import, print_function

import logging

_logger = logging.getLogger("ant.easy.exception")


class AntException(Exception):
    pass


class TransferFailedException(AntException):
    pass


class ReceiveFailedException(AntException):
    pass


class ReceiveFailException(AntException):
    pass
