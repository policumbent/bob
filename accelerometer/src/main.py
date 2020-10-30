from src.accelerometer import Accelerometer
import time
import json

from src.settings import Settings
from src.mqtt import MqttSensor


def signal(s):
    pass


def new_settings(s):
    pass


def send_message(message, priority):
    print(message, priority)


def start():
    print('Starting')
    settings = Settings({})
    accelerometer = Accelerometer(settings)
    mqtt = MqttSensor('192.168.1.20', 1883, 'accelerometer', signal, new_settings)
    while True:
        mqtt.publish(json.dumps(accelerometer.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
