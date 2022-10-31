import sys
from time import sleep
import json
from .settings import Settings
from core.mqtt import MqttSensor
from core.alert import Alert
from core.message import Message

mqtt: MqttSensor


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    pass


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting LED controller')
    settings = Settings({
        'mode': 0
    }, 'LED')
    settings.load()
    global mqtt
    mqtt = MqttSensor(sys.argv[1], 1883, 'LED', [''], settings, message_handler)
    while True:
        mqtt.publish(str(settings.mode))
        sleep(1)


if __name__ == '__main__':
    start()
