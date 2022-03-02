import sys
from time import sleep
import json
from .settings import Settings
from core.mqtt import MqttSensor
from core.alert import Alert
from core.message import Message
from .example_sensor import ExampleSensor

mqtt: MqttSensor
hall_sensor: ExampleSensor


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        hall_sensor.signal(message.decode())
#$$message handler$$#

def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting ExampleSensor')
    settings = Settings({
        'example_setting': False
    })
    global hall_sensor
    example_sensor = ExampleSensor(settings, send_alert, send_message)
    global mqtt
    #$$mqtt start$$#
    while True:
        mqtt.publish(json.dumps(example_sensor.export()))
        sleep(1)


if __name__ == '__main__':
    start()
