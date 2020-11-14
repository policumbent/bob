import time
import json
from .settings import Settings
from .mqtt import MqttConsumer
from .message import Message
from .alert import Alert
from .gear import Gear

settings = Settings(
    {
        'gear': {
            'up_positions_s1': [49, 60, 70, 78, 92, 99, 108, 120, 131, 141, 170],
            'up_positions_s2': [171, 156, 143, 133, 115, 106, 93, 78, 64, 51, 12],
            'down_positions_s1': [49, 63, 71, 78, 88, 97, 107, 118, 131, 141, 153],
            'down_positions_s2': [171, 152, 142, 132, 120, 108, 94, 80, 64, 51, 35]
        }
    })
mqtt: MqttConsumer
gear: Gear


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def message_handler(topic, message):
    if topic == 'sensors/gpio':
        # todo: gestire parsing error
        json_message = json.loads(message)
        gear.shift(json_message['message'])
        mqtt.publish(json.dumps(gear.export()))


def send_pressed(message: int):
    m = {'message': message}
    mqtt.publish(json.dumps(m))


def start():
    print('Starting Communication')
    settings.load()
    global mqtt
    mqtt = MqttConsumer('192.168.1.20', 1883, 'gear', ['gpio'],
                        settings, message_handler)
    mqtt.publish_settings(settings)
    global gear
    gear = Gear(send_message, settings)
    while True:
        mqtt.publish(json.dumps(gear.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
