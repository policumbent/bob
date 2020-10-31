from src.accelerometer import Accelerometer
import time
import json

from .settings import Settings
from ...common_files.mqtt import MqttSensor


def signal(s):
    pass


def new_settings(s):
    pass


def send_message(message, priority):
    print(message, priority)


def start():
    print('Starting accelerometer')
    settings = Settings({})
    accelerometer = Accelerometer(settings)
    mqtt = MqttSensor('192.168.1.20', 1883, 'accelerometer', signal, new_settings)
    while True:
        mqtt.publish(json.dumps(accelerometer.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
