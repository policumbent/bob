from __future__ import absolute_import, print_function

import collections
import threading
import logging

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

from ..base.ant import Ant
from ..base.message import Message
from ..easy.channel import Channel
from ..easy.filter import wait_for_event, wait_for_response, wait_for_special

_logger = logging.getLogger("ant.easy.node")


class Node:
    def __init__(self, network=None, key=None):
        self._responses_cond = threading.Condition()
        self._responses = collections.deque()
        self._event_cond = threading.Condition()
        self._events = collections.deque()

        self._datas = queue.Queue()

        self._network = network
        self._key = key

        self.channels = {}

        self.ant = Ant()

        self._running = True

        self._worker_thread = threading.Thread(target=self._worker, name="ant.easy")
        self._worker_thread.start()

    def __enter__(self):
        if self._network is None or self._key is None:
            raise KeyError

        self.set_network_key(self._network, self._key)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # In this block of code no exception handling is performed so the exceptions are propagated
        self.stop()

    def new_channel(self, ctype, network_number=0x00):
        size = len(self.channels)
        channel = Channel(size, self, self.ant)
        self.channels[size] = channel
        channel._assign(ctype, network_number)
        return channel

    def request_message(self, messageId):
        _logger.debug("requesting message %#02x", messageId)
        self.ant.request_message(0, messageId)
        _logger.debug("done requesting message %#02x", messageId)
        return self.wait_for_special(messageId)

    def set_network_key(self, network, key):
        self.ant.set_network_key(network, key)
        return self.wait_for_response(Message.ID.SET_NETWORK_KEY)

    def wait_for_event(self, ok_codes):
        return wait_for_event(ok_codes, self._events, self._event_cond)

    def wait_for_response(self, event_id):
        return wait_for_response(event_id, self._responses, self._responses_cond)

    def wait_for_special(self, event_id):
        return wait_for_special(event_id, self._responses, self._responses_cond)

    def _worker_response(self, channel, event, data):
        self._responses_cond.acquire()
        self._responses.append((channel, event, data))
        self._responses_cond.notify()
        self._responses_cond.release()

    def _worker_event(self, channel, event, data):
        if event == Message.Code.EVENT_RX_BURST_PACKET:
            self._datas.put(("burst", channel, data))
        elif event == Message.Code.EVENT_RX_BROADCAST:
            self._datas.put(("broadcast", channel, data))
        else:
            self._event_cond.acquire()
            self._events.append((channel, event, data))
            self._event_cond.notify()
            self._event_cond.release()

    def _worker(self):
        self.ant.response_function = self._worker_response
        self.ant.channel_event_function = self._worker_event

        # TODO: check capabilities
        self.ant.start()

    def _main(self):
        while self._running:
            try:
                (data_type, channel, data) = self._datas.get(True, 1.0)
                self._datas.task_done()

                if data_type == "broadcast":
                    self.channels[channel].on_broadcast_data(data)
                    # print(f"Channel {channel} pushed broadcast {data}")
                elif data_type == "burst":
                    self.channels[channel].on_burst_data(data)
                    # print(f"Channel {channel} pushed burst {data}")
                else:
                    _logger.warning("Unknown data type '%s': %r", data_type, data)
            except queue.Empty as e:
                pass

    def start(self):
        self._main()

    def stop(self):
        if self._running:
            _logger.debug("Stoping ant.easy")
            self._running = False
            self.ant.stop()
            self._worker_thread.join()
