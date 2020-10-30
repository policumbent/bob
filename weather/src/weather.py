# pylint: disable=import-error

import json
import threading

# import Adafruit_DHT

from threading import Thread
import time
import board
import digitalio
from busio import SPI
from board import SCK, MOSI, MISO, D5, D9, D10, D11
from digitalio import DigitalInOut as dgio
from adafruit_bmp280 import Adafruit_BMP280_SPI

from src.sensors.sensor import Sensor
from src.utility.settings import Settings
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

    def __init__(self, settings: Settings, loop_delay: int = 1):
        self._bus = SMBus(1)
        self._settings = settings
        self._settings_lock = threading.Lock()
        self._value_lock = threading.Lock()
        self._sensor = BME280(i2c_dev=self._bus)
        self._data = dict()
        self._data["wind_speed"] = 100
        print('Ciaooooooooo')
        self._worker = Thread(target=self._loop, daemon=False)
        self._worker.start()

    def _loop(self):
        while True:
            with self._value_lock:
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
        with self._settings_lock:
            self._settings = settings

    def export(self):
        with self._value_lock:
            return self._data.copy()
