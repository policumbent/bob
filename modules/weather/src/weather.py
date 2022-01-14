# pylint: disable=import-error

import json
import threading

# import Adafruit_DHT

from threading import Thread
import time

from .common_files.sensor import Sensor
from .settings import Settings
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280
# SENSOR = Adafruit_DHT.DHT22
PIN = '4'


class Weather(Sensor):

    def signal(self, value: str):
        pass

    def __init__(self, settings: Settings,  send_alert,
                 send_message, loop_delay: int = 1):
        self._bus = SMBus(1)
        self._settings = settings
        self._send_alert = send_alert
        self._send_message = send_message
        # self._settings_lock = threading.Lock()
        # self._value_lock = threading.Lock()
        self._sensor = BME280(i2c_dev=self._bus)
        self._data = dict()
        self._worker = Thread(target=self._loop, daemon=False)
        self._worker.start()

    def _loop(self):
        while True:
            self._data["temperature"] = round(self._sensor.get_temperature(), 2)
            self._data["pressure"] = round(self._sensor.get_pressure(), 2)
            self._data["humidity"] = round(self._sensor.get_humidity(), 2)
            # print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'
            #       .format(self._data["temperature"],
            #               self._data["pressure"],
            #               self._data["humidity"]))
            time.sleep(1)

    @property
    def data(self):
        return self._data

    def update_settings(self, settings: Settings):
        self._settings = settings

    def export(self):
        return self._data.copy()