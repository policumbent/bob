import abc
from .common_settings import CommonSettings


class Sensor:
    # todo: andrebbero gestiti i lock in lettura
    @abc.abstractmethod
    def export(self):
        pass
    #
    # @abc.abstractmethod
    # def update_settings(self, settings: CommonSettings):
    #     pass

    @abc.abstractmethod
    def signal(self, value: str):
        pass
