from .ant_manager import Ant
import time
import json

from .heartrate import HeartRate
from .powermeter import Powermeter
from .settings import Settings
from ...common_files.mqtt import MqttSensor
from .speed import Speed
from .timer import Timer


def signal(s):
    pass


def new_settings(s):
    pass


def send_message(message, priority):
    print(message, priority)


def start():
    print('Starting')
    settings = Settings({})
    timer = Timer()
    hr = HeartRate(settings)
    speed = Speed(send_message, settings, timer)
    powermeter = Powermeter(send_message, settings)
    Ant(send_message, hr, speed, powermeter)
    mqtt = MqttSensor('192.168.1.20', 1883, 'ant', signal, new_settings)
    while True:
        v = dict()
        v.update(timer.export())
        v.update(hr.export())
        v.update(speed.export())
        v.update(powermeter.export())
        mqtt.publish(json.dumps(v))
        time.sleep(1)


if __name__ == '__main__':
    start()
