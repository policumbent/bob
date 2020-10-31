import abc
from ant.src.settings import Settings


class Sensor:
    # todo: andrebbero gestiti i lock in lettura
    @abc.abstractmethod
    def export(self):
        pass

    @abc.abstractmethod
    def update_settings(self, settings: Settings):
        pass

    @abc.abstractmethod
    def signal(self, value: str):
        pass
