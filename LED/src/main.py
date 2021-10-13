import sys
from time import sleep
import json
from .settings import Settings
from .common_files.mqtt import MqttSensor
from .common_files.alert import Alert
from .common_files.message import Message

mqtt: MqttSensor


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        hall_sensor.signal(message.decode())


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting LED controller')
    settings = Settings({
        'mode': 0
    })
    MqttSensor(sys.argv[1], 1883, 'LED', [''], settings, message_handler)
    while True:
        sleep(1)


if __name__ == '__main__':
    start()
