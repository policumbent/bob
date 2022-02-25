import RPi.GPIO as GPIO
import time
from core.sensor import Sensor
from .settings import Settings


class HallSensor(Sensor):
    def export(self):
        return {
            'speed_2': self.speed,
            'distance_2': self.distance
        }

    def signal(self, value: str):
        if value == 'reset':
            self.counter = 0

    def __init__(self, settings: Settings, send_alert, send_message):
        self.pin = settings.pin
        self.__settings: Settings = settings
        self.timer = -1
        self.frequency = 0
        self.counter = 0
        self._last_rx = time.time()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.clock)  # passing from HIGH to LOW

    def __del__(self):
        GPIO.cleanup()

    def clock(self, channel):
        self.counter += 1
        if self.timer == -1:
            self.timer = time.time()
        else:
            tme = time.time()
            period = tme - self.timer
            self.timer = tme
            self.calc_freq(period)
            self.print_status()  # per il debugging

    def calc_freq(self, period):
        if period >= 0.036:
            self.frequency = 1 / period

    @property
    def speed(self):
        if (time.time() - self.timer) > 5.0:
            return 0.0
        return round(self.__settings.circumference * self.frequency * 3.6 / 1000, 2)  # circumference * frequency

    @property
    def distance(self):
        return round(self.counter * self.__settings.circumference / pow(10, 6), 2)

    def get_rpm(self):
        return self.frequency * 60

    def print_status(self):
        print(f" freq: {self.get_rpm(): .2f} giri/min vel: {self.speed: .2f} km/h dist: {self.distance: .2f} m")

    def print_pin_status(self):
        print(GPIO.input(self.pin))  # prints the status of the pin: HIGH(1)/LOW(0)
