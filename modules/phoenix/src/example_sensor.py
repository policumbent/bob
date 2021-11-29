from .common_files.sensor import Sensor
from .settings import Settings


class ExampleSensor(Sensor):
    def export(self):
        return {
            'example': 1
        }

    def signal(self, value: str):
        pass

    def __init__(self, settings: Settings, send_alert, send_message):
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
