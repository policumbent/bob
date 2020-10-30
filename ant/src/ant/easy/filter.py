from __future__ import absolute_import, print_function

import logging

from ..base.message import Message
from ..easy.exception import AntException, TransferFailedException

_logger = logging.getLogger("ant.easy.filter")


def wait_for_message(match, process, queue, condition):
    """
    Wait for a specific message in the *queue* guarded by the *condition*
    matching the function *match* (which is a function that takes a
    message as a parameter and returns a boolean). The messages is
    processed by the *process* function before returning it.
    """
    _logger.debug("wait for message matching %r", match)
    condition.acquire()
    for _ in range(10):
        _logger.debug("looking for matching message in %r", queue)
        # _logger.debug("wait for response to %#02x, checking", mId)
        for message in queue:
            if match(message):
                _logger.debug(" - response found %r", message)
                queue.remove(message)
                condition.release()
                return process(message)
            elif message[1] == 1 and message[2][0] in [Message.Code.EVENT_TRANSFER_TX_FAILED,
                                                       Message.Code.EVENT_RX_FAIL_GO_TO_SEARCH]:
                _logger.warning("Transfer send failed:")
                _logger.warning(message)
                queue.remove(message)
                condition.release()
                raise TransferFailedException()
        _logger.debug(" - could not find response matching %r", match)
        condition.wait(1.0)
    condition.release()
    raise AntException("Timed out while waiting for message")


def wait_for_event(ok_codes, queue, condition):
    def match(params):
        channel, event, data = params
        return data[0] in ok_codes

    def process(params):
        return params

    return wait_for_message(match, process, queue, condition)


def wait_for_response(event_id, queue, condition):
    """
    Waits for a response to a specific message sent by the channel response
    message, 0x40. It's expected to return RESPONSE_NO_ERROR, 0x00.
    """

    def match(params):
        channel, event, data = params
        return event == event_id

    def process(params):
        channel, event, data = params
        if data[0] == Message.Code.RESPONSE_NO_ERROR:
            return params
        else:
            raise Exception("Responded with error " + str(data[0])
                            + ":" + Message.Code.lookup(data[0]))

    return wait_for_message(match, process, queue, condition)


def wait_for_special(event_id, queue, condition):
    """
    Waits for special responses to messages such as Channel ID, ANT
    Version, etc. This does not throw any exceptions, besides timeouts.
    """

    def match(params):
        channel, event, data = params
        return event == event_id

    def process(params):
        return params

    return wait_for_message(match, process, queue, condition)
