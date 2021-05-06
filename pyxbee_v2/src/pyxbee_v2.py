import json

import serial

from .settings import Settings
from .common_files.bikeData import BikeData
from datetime import datetime


class PyxbeeV2:
    def __init__(self, settings: Settings, send_alert, send_message):
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        self.__serial: serial.Serial = serial.Serial('/dev/ttyUSB0', 115200)

    @staticmethod
    def format_data(bike_data_dict: dict) -> str:
        try:
            dt = datetime.strptime(bike_data_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
            bike_data_dict['timestamp'] = int((dt - datetime(1970, 1, 1)).total_seconds())
            print(bike_data_dict['timestamp'])
        except ValueError as e:
            print(e)
            bike_data_dict['timestamp'] = 0
        bike_data_str_list = [str(d) for d in bike_data_dict.values()]
        return ','.join(bike_data_str_list) + '\n'

    def send_data(self, bike_data: BikeData):
        message = self.format_data(bike_data.to_json())
        self.__serial.write(message.encode('utf-8'))
        print(message)
        message = message[:-1]
        message_list = message.split(',')
        keys = bike_data.get_keys()
        print(keys)
        res = {keys[i]: message_list[i] for i in range(len(keys))}
        print(json.dumps(res, indent=4))

