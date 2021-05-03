from .common_files.sensor import Sensor
from .settings import Settings


class ExampleSensor(Sensor):
    def export(self):
        return {
            'speed_2': self.__speed,
            'distance_2':self.__distance
        }

    def signal(self, value: str):
        if value == 'reset':
            self.__distance=0

    def __init__(self, settings: Settings, send_alert, send_message):
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        self.__speed = 0
        self.__distance = 0
