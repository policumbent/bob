import threading
from gpiozero import CPUTemperature
from src.communication import Notice
from src.sensors.sensor import Sensor
from src.utility.settings import Settings


class RaspySensors(Sensor):
    def __init__(self, messages: Message, settings: Settings):
        self._temperature = CPUTemperature()
        self._settings = settings
        self._message = messages
        self._settings_lock = threading.Lock()

    def export(self):
        with self._settings_lock:
            max_t = self._settings.max_temp
        if self.temperature > self._settings.max_temp:
            mex = "Temperatura CPU alta (" + str(round(self.temperature)) + "°C)"
            self._message.set(mex, MexPriority.high)
            Notice.new(mex)
        return {'temperature': self.temperature}

    def update_settings(self, settings: Settings):
        with self._settings_lock:
            self._settings = settings

    @property
    def temperature(self):
        return self._temperature.temperature
