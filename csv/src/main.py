import sys
from time import sleep
import json
from .settings import Settings
from .common_files.mqtt import MqttConsumer
from .common_files.alert import Alert
from .common_files.message import Message
from .common_files.bikeData import BikeData
from .csv import Csv

mqtt: MqttConsumer
bike_data: BikeData


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        example_sensor.signal(message.decode())
    try:
        if topic == 'sensors/manager':
            manager_dict: dict = json.loads(message)
            bike_data.set_manager(manager_dict)
        if topic == 'sensors/ant':
            ant_dict: dict = json.loads(message)
            bike_data.set_ant(ant_dict)
        if topic == 'sensors/gps':
            gps_dict: dict = json.loads(message)
            bike_data.set_gps(gps_dict)
        if topic == 'sensors/hall_sensor':
            hall_sensor_dict: dict = json.loads(message)
            bike_data.set_hall_sensor(hall_sensor_dict)
        if topic == 'sensors/gear':
            gear_dict: dict = json.loads(message)
            bike_data.set_gear(gear_dict)
        if topic == 'sensors/accelerometer':
            accelerometer_dict: dict = json.loads(message)
            bike_data.set_accelerometer(accelerometer_dict)
    except Exception as e:
        print(e)


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting Csv')
    settings = Settings({})
    global bike_data
    bike_data = BikeData(['manager', 'ant', 'gps', 'hall_sensor', 'gear', 'accelerometer'])
    csv = Csv(settings, send_alert, send_message)
    global mqtt
    mqtt = MqttConsumer(sys.argv[1], 1883, 'csv', ['manager', 'ant', 'gps', 'hall_sensor', 'gear', 'accelerometer'],
                        ['reset'], settings, message_handler)
    while True:
        sleep(1)


if __name__ == '__main__':
    start()
