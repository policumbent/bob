import json

from serial import Serial
from .settings import Settings
from .common_files.bikeData import BikeData
from datetime import datetime

keys2bike = ["wind_speed", "wind_direction", "temperature", "humidity"]


class PyxbeeV2:
    def __init__(self, settings: Settings, send_alert, send_message):
        keys2bike.sort()
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        self.__serial: Serial = Serial('/dev/ttyUSB0', 115200)

    @staticmethod
    def format_data(bike_data_dict: dict) -> str:
        try:
            dt = datetime.strptime(bike_data_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
            bike_data_dict['timestamp'] = int((dt - datetime(1970, 1, 1)).total_seconds())
        except ValueError as e:
            print(e)
            bike_data_dict['timestamp'] = 0
        bike_data_str_list = [str(d) for d in bike_data_dict.values()]
        return ','.join(bike_data_str_list) + '\n'

    def send_data(self, bike_data: BikeData):
        message = self.format_data(bike_data.to_json())
        self.__serial.write(message.encode('utf-8'))
        # print(message)
        # message = message[:-1]
        # message_list = message.split(',')
        # keys = bike_data.get_keys()
        # print(keys)
        # res = {keys[i]: message_list[i] for i in range(len(keys))}
        # print(json.dumps(res, indent=4))

    def get_data(self) -> dict:
        try:
            if self.__serial.in_waiting:
                line = self.__serial.readline().decode()
                data_list = line.split(',')
                print(keys2bike)
                res = {keys2bike[i]: data_list[i] for i in range(len(keys2bike))}
                print(json.dumps(res, indent=4))
                return res
        except Exception as e:
            print(e)
        return {}
