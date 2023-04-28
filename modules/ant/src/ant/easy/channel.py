from __future__ import absolute_import, print_function

import logging
from typing import List

# import threading
from ..base.message import Message
from ..easy.exception import TransferFailedException
from ..easy.filter import wait_for_event, wait_for_response, wait_for_special

_logger = logging.getLogger("ant.easy.channel")


class Channel:
    class Type:
        BIDIRECTIONAL_RECEIVE = 0x00
        BIDIRECTIONAL_TRANSMIT = 0x10

        SHARED_BIDIRECTIONAL_RECEIVE = 0x20
        SHARED_BIDIRECTIONAL_TRANSMIT = 0x30

        UNIDIRECTIONAL_RECEIVE_ONLY = 0x40
        UNIDIRECTIONAL_TRANSMIT_ONLY = 0x50

    def __init__(self, id, node, ant):
        self.id = id
        self._node = node
        self._ant = ant

    def wait_for_event(self, ok_codes):
        return wait_for_event(ok_codes, self._node._events, self._node._event_cond)

    def wait_for_response(self, event_id):
        return wait_for_response(event_id, self._node._responses, self._node._responses_cond)

    def wait_for_special(self, event_id):
        return wait_for_special(event_id, self._node._responses, self._node._responses_cond)

    def _assign(self, channelType, networkNumber):
        self._ant.assign_channel(self.id, channelType, networkNumber)
        return self.wait_for_response(Message.ID.ASSIGN_CHANNEL)

    def _unassign(self):
        pass

    def open(self):
        self._ant.open_channel(self.id)
        print("Channel open: " + str(self.id))
        return self.wait_for_response(Message.ID.OPEN_CHANNEL)

    # #TODO_: DA TESTARE
    # def close(self):
    #     self._ant.close_channel(self.id)
    #     print("Channel close: " + str(self.id))
    #     return self.wait_for_response(Message.ID.CLOSE_CHANNEL)

    def set_id(self, deviceNum, deviceType, transmissionType):
        self._ant.set_channel_id(self.id, deviceNum, deviceType, transmissionType)
        return self.wait_for_response(Message.ID.SET_CHANNEL_ID)

    def set_period(self, messagePeriod):
        self._ant.set_channel_period(self.id, messagePeriod)
        return self.wait_for_response(Message.ID.SET_CHANNEL_PERIOD)

    def set_search_timeout(self, timeout):
        self._ant.set_channel_search_timeout(self.id, timeout)
        return self.wait_for_response(Message.ID.SET_CHANNEL_SEARCH_TIMEOUT)

    def set_rf_freq(self, rfFreq):
        self._ant.set_channel_rf_freq(self.id, rfFreq)
        return self.wait_for_response(Message.ID.SET_CHANNEL_RF_FREQ)

    def set_search_waveform(self, waveform):
        self._ant.set_search_waveform(self.id, waveform)
        return self.wait_for_response(Message.ID.SET_SEARCH_WAVEFORM)

    def request_message(self, messageId):
        _logger.debug("requesting message %#02x", messageId)
        self._ant.request_message(self.id, messageId)
        _logger.debug("done requesting message %#02x", messageId)
        return self.wait_for_special(messageId)

    def request_closed(self):
        return self.wait_for_special(Message.ID.EVENT_CHANNEL_CLOSED)

    def send_acknowledged_data(self, data):
        try:
            _logger.debug("send acknowledged data %s", self.id)
            self._ant.send_acknowledged_data(self.id, data)
            self.wait_for_event([Message.Code.EVENT_TRANSFER_TX_COMPLETED])
            _logger.debug("done sending acknowledged data %s", self.id)
        except TransferFailedException:
            _logger.warning("failed to send acknowledged data %s, retrying", self.id)
            self.send_acknowledged_data(data)

    def send_burst_transfer_packet(self, channelSeq, data, first):
        _logger.debug("send burst transfer packet %s", data)
        self._ant.send_burst_transfer_packet(channelSeq, data, first)

    def send_burst_transfer(self, data):
        try:
            _logger.debug("send burst transfer %s", self.id)
            self._ant.send_burst_transfer(self.id, data)
            self.wait_for_event([Message.Code.EVENT_TRANSFER_TX_START])
            self.wait_for_event([Message.Code.EVENT_TRANSFER_TX_COMPLETED])
            _logger.debug("done sending burst transfer %s", self.id)
        except TransferFailedException:
            _logger.warning("failed to send burst transfer %s, retrying", self.id)
            self.send_burst_transfer(data)

    def send_broadcast_data(self, data : List[int]):
        _logger.debug("send broadcast data %s", self.id)
        self._ant.send_broadcast_data(self.id, data)
