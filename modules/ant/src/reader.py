from abc import ABC, abstractmethod

from .ant.easy.channel import Channel
from .ant.easy.node import Node

_DEFAULT_CHANNEL_TYPE = Channel.Type.BIDIRECTIONAL_RECEIVE


class AntReader(ABC):
    NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]

    def __init__(self, node: Node, sensor_id=None, channel_type=None) -> None:
        self._node = node
        self._channel = None
        self._sensor_id = sensor_id

        if channel_type:
            self._channel = self._create_channel(type)
        

    def _create_channel(self, type=_DEFAULT_CHANNEL_TYPE):
        self._node.new_channel(type)

    def __del__(self):
        # self._channel.close()
        pass

    @abstractmethod
    def _init_channel(self):
        pass

    @abstractmethod
    def _receve_new_data(self, data):
        pass

    @abstractmethod
    def read_data():
        pass
