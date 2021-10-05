import json

from serial import Serial
from .settings import Settings
from .common_files.bikeData import BikeData
from datetime import datetime

keys2bike = ["wind_speed", "wind_direction", "temperature", "humidity"]


class PyxbeeV3:
    def __init__(self, settings: Settings, send_alert, send_message):
        keys2bike.sort()
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        # self.__serial_open = False
        # self.__serial = None
        # self.__open_serial()

    # def __open_serial(self):
    #     try:
    #         self.__serial: Serial = Serial('/dev/ttyUSB1', 115200)
    #         self.__serial_open = True
    #         print('Serial LORA open')
    #     except Exception as e:
    #         print(e)
    #         self.__serial_open = False

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

    def get_mqtt_data(self, bike_data: BikeData):
        data = bike_data.to_json()
        message = self.format_data(data)
        return message

        # print(message)
        # message = message[:-1]
        # message_list = message.split(',')
        # keys = bike_data.get_keys()
        # print(keys)
        # res = {keys[i]: message_list[i] for i in range(len(keys))}
        # print(json.dumps(res, indent=4))

    # def get_data(self) -> dict:
    #     try:
    #         if self.__serial.in_waiting:
    #             line = self.__serial.readline().decode()
    #             data_list = line.split(',')
    #             print(keys2bike)
    #             res = {keys2bike[i]: data_list[i] for i in range(len(keys2bike))}
    #             print(json.dumps(res, indent=4))
    #             return res
    #     except Exception as e:
    #         print(e)
    #     return {}
