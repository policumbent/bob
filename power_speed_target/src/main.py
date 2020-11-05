import time
import json
from .settings import Settings
from .mqtt import MqttConsumer
from .message import Message
from .power_speed_target import PowerSpeedTarget

settings = Settings({
    'speed_power_target_csv': 'test_Vittoria.csv',
})
distance = 0


def message_handler(topic, message):
    pass


def start():
    print('Starting speed_power_target')

    settings.load()
    mqtt = MqttConsumer('192.168.1.20', 1883, 'speed_power_target', ['ant'], settings, message_handler)
    target: PowerSpeedTarget = PowerSpeedTarget(settings)
    while True:
        # print(data)
        mqtt.publish(data)
        time.sleep(1)


if __name__ == '__main__':
    start()
