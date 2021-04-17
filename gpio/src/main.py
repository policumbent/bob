import time
import json
import sys
from .settings import Settings
from .mqtt import MqttRemote
from .message import Message
from .alert import Alert
from .gpio import Gpio, GpioMessage
settings = Settings({})
mqtt: MqttRemote


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def message_handler(topic, message):
    pass


def send_pressed(message: int):
    if message == GpioMessage.reset:
        mqtt.publish_signal('reset')
    else:
        m = {'message': message}
        mqtt.publish(json.dumps(m))


def start():
    print('Starting GPIO')
    settings.load()
    global mqtt
    mqtt = MqttRemote(sys.argv[1], 1883, 'gpio', [], [], settings, message_handler)
    Gpio(send_message, send_alert, send_pressed)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    start()
