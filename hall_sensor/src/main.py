import sys
from time import sleep
import json
from .settings import Settings
from .common_files.mqtt import MqttSensor
from .common_files.alert import Alert
from .common_files.message import Message
from .hall_sensor import HallSensor

mqtt: MqttSensor
hall_sensor: HallSensor


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
    print('Starting ExampleSensor')
    settings = Settings({
        'pin': 24,
        'circumference': 1450
    })
    global hall_sensor
    hall_sensor = HallSensor(settings, send_alert, send_message)
    global mqtt
    mqtt = MqttSensor(sys.argv[1], 1883, 'hall_sensor', ['reset'], settings, message_handler)
    while True:
        mqtt.publish(json.dumps(hall_sensor.export()))
        sleep(1)


if __name__ == '__main__':
    start()
