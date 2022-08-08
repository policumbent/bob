from abc import ABC, abstractmethod
from enum import Enum

from .ant.easy.channel import Channel
from .ant.easy.node import Node

from core import time


_DEFAULT_CHANNEL_TYPE = Channel.Type.BIDIRECTIONAL_RECEIVE


class DeviceTypeID(Enum):
    powermeter = 11
    heartrate = 120
    speed = 123
    speed_cadence = 121


class AntDevice(ABC):
    NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]

    def __init__(self, node: Node, sensor_id=None, channel_type=None) -> None:
        self._node = node
        self._channel = None
        self._sensor_id = sensor_id

        # sensor data
        self._payload = None
        self._received_data = False
        self._last_data_read = None

        if channel_type:
            self._channel = self._create_channel(channel_type)

    def __del__(self):
        # self._channel.close()
        pass

    def _create_channel(self, type=_DEFAULT_CHANNEL_TYPE):
        return self._node.new_channel(type)

    def _current_time(self):
        return time._unix_time()

    def _elapsed_time(self):
        return self._current_time() - self._last_data_read

    def _is_active(self, time_sec=5):
        return self._last_data_read and self._elapsed_time() < time_sec

    @abstractmethod
    def _init_channel(self):
        pass

    @abstractmethod
    def _receive_new_data(self, data):
        pass

    @abstractmethod
    def read_data(self):
        pass
