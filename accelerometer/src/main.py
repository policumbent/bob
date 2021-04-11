from .accelerometer import Accelerometer
import time
import json
import sys
from .settings import Settings
from .mqtt import MqttSensor
from .alert import Alert
from .message import Message
import os

mqtt: MqttSensor
accelerometer: Accelerometer


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        accelerometer.signal(message.decode())


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting accelerometer')
    settings = Settings({
        'accelerometer_local_csv': False
    })
    os.system('i2cdetect -y 1')
    global accelerometer
    accelerometer = Accelerometer(settings, send_alert, send_message)
    global mqtt
    mqtt = MqttSensor(sys.argv[1], 1883, 'accelerometer', settings, message_handler)
    while True:
        mqtt.publish(json.dumps(accelerometer.export()))
        # print(accelerometer.export())
        time.sleep(1)


if __name__ == '__main__':
    start()
