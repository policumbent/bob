import threading
from gpiozero import CPUTemperature
from .sensor import Sensor
from .settings import Settings
from .message import Message, MexPriority, MexType
from .alert import Alert, AlertPriority


class RaspySensors(Sensor):
    def signal(self, value: str):
        pass

    def __init__(self, send_message, send_alert, settings: Settings):
        self._temperature = CPUTemperature()
        self._settings = settings
        self._send_message = send_message
        self._send_alert = send_alert
        self._settings_lock = threading.Lock()

    def export(self):
        with self._settings_lock:
            max_t = self._settings.max_temp
        if self.temperature > max_t:
            mex = "Temperatura CPU alta (" + str(round(self.temperature)) + "°C)"
            self._send_message(Message(mex, MexPriority.high, MexType.default, 1, 1))
            self._send_alert(Alert(mex, AlertPriority.very_high))
        return {'temperature': self.temperature}

    def update_settings(self, settings: Settings):
        with self._settings_lock:
            self._settings = settings

    @property
    def temperature(self):
        return self._temperature.temperature
