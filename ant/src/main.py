from threading import Thread

from .ant_manager import Ant
import time
import sys
import json
from .message import Message
from .heartrate import HeartRate
from .powermeter import Powermeter
from .settings import Settings
from .mqtt import MqttSensor
from .speed import Speed
from .timer import Timer

settings = Settings({
    'hour_record': False,
    'run_length': 8046,
    'trap_length': 200,
    'hr_sensor_id': 0,
    'speed_sensor_id': 0,
    'power_sensor_id': 0,
    'circumference': 1450,
    'average_power_time': 3
})
mqtt: MqttSensor


def message_handler(topic, message):
    pass


def new_settings(s):
    pass


def send_message(message: Message):
    print(message.text)
    mqtt.publish_message(message)


def loop(timer, hr, speed, powermeter):
    while True:
        v = dict()
        # v.update(timer.export())
        v.update(hr.export())
        v.update(speed.export())
        v.update(powermeter.export())
        print(v)
        mqtt.publish(json.dumps(v))
        time.sleep(1)


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting ANT')

    timer = Timer()
    hr = HeartRate(settings)
    speed = Speed(send_message, settings, timer)
    powermeter = Powermeter(send_message, settings)
    worker_thread = Thread(target=loop, args=(timer, hr, speed, powermeter), daemon=True)
    worker_thread.start()
    Ant(send_message, hr, speed, powermeter)


mqtt = MqttSensor(sys.argv[1], 1883, 'ant', settings, message_handler)

if __name__ == '__main__':
    start()
