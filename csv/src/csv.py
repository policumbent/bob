from .common_files.sensor import Sensor
from .settings import Settings
import csv


class Csv:
    def signal(self, value: str):
        pass

    def __init__(self, settings: Settings, send_alert, send_message):
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        self.__csv_file = None
        self.__csv_writer: csv.DictWriter = None

    def start_csv(self):
        self.__csv_file = ope
        self.__csv_writer

        pass

    def write_data(self, bike_data: BikeData):
        pass
