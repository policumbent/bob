import time
import json
import sys
from .settings import Settings
from .common_files.mqtt import MqttSensor
from .common_files.alert import Alert
from .common_files.message import Message
from .weather import Weather

import os

mqtt: MqttSensor
weather: Weather


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        weather.signal(message.decode())


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting indoor weather')
    settings = Settings({})
    os.system('i2cdetect -y 1')
    global weather
    weather = Weather(settings, send_alert, send_message)
    global mqtt
    mqtt = MqttSensor(sys.argv[1], 1883, 'indoor_weather', [], settings, message_handler)
    time.sleep(1)
    while True:
        mqtt.publish(json.dumps(weather.export()))
        # print(accelerometer.export())
        time.sleep(1)


if __name__ == '__main__':
    start()
