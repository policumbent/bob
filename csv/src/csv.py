from .settings import Settings
from .common_files.bikeData import BikeData
from csv import DictWriter
from datetime import datetime
from os import makedirs

class Csv:
    def signal(self, value: str):
        if value == 'reset':
            self.close_csv()
            self.start_csv()

    def __init__(self, settings: Settings, send_alert, send_message, bike_data: BikeData):
        self.__settings = settings
        self.__send_alert = send_alert
        self.__send__message = send_message
        self.__csv_file = None
        self.__csv_writer: DictWriter = None
        self.__bike_data: BikeData = bike_data
        self.start_csv()

    def __del__(self):
        self.close_csv()

    def start_csv(self):
        makedirs('./data', exist_ok=True)
        file_name = datetime.now().strftime('%y-%m-%d_%H:%M:%S')
        gps_timestamp = self.__bike_data.timestamp
        print(gps_timestamp, gps_timestamp != '00-01-01 00:00:00', gps_timestamp != '20-- ::')
        if gps_timestamp != '00-01-01 00:00:00' and gps_timestamp != '20-- ::':
            file_name += '-' + gps_timestamp.replace(' ', '_')
        self.__csv_file = open(f'./data/{file_name}.csv', 'w')
        keys: list = list(self.__bike_data.to_json().keys())
        print(keys)
        print(type(keys))
        self.__csv_writer = DictWriter(self.__csv_file, fieldnames=keys)
        self.__csv_writer.writeheader()

    def close_csv(self):
        self.__csv_file.close()

    def write_data(self, bike_data: BikeData):
        # print('row', bike_data.to_json())
        print(self.__csv_writer.writerow(bike_data.to_json()))
