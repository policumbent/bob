from threading import Thread

from core.mqtt import MqttConsumer
from core.message import Message
from .ant_manager import Ant
import time
import sys
import json
from .heartrate import HeartRate
from .powermeter import Powermeter
from .settings import Settings
from .speed import Speed

settings = Settings({
    'hour_record': False,
    'run_length': 8046,
    'trap_length': 200,
    'hr_sensor_id': 0,
    'speed_sensor_id': 0,
    'power_sensor_id': 0,
    'circumference': 1450,
    'average_power_time': 3
}, 'ant')
mqtt: MqttConsumer
sensors: dict = dict()


def message_handler(topic, message: bytes):
    if topic == 'signals':
        for e in sensors:
            sensors[e].signal(message)
        return
    try:
        if topic == 'sensors/manager':
            json_message = json.loads(message)
            if sensors.__contains__('speed'):
                sensors['speed'].time_int = int(json_message['time_int'])
    except Exception as e:
        print(e)


def send_message(message: Message):
    print(message.text)
    mqtt.publish_message(message)


def loop():
    while True:
        v = dict()
        for e in sensors:
            v.update(sensors[e].export())
        # # v.update(timer.export())
        # v.update(hr.export())
        # v.update(speed.export())
        # v.update(powermeter.export())
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
    settings.load()
    print(settings.values)
    # sensors['timer'] = Timer()
    sensors['hr'] = HeartRate(settings)
    sensors['speed'] = Speed(send_message, settings)
    sensors['powermeter'] = Powermeter(send_message, settings)
    worker_thread = Thread(
        target=loop,
        daemon=True)
    worker_thread.start()
    Ant(send_message, sensors['hr'], sensors['speed'], sensors['powermeter'])


mqtt = MqttConsumer(sys.argv[1], 1883, 'ant', ['manager'], ['powermeter_calibration', 'reset'],
                    settings, message_handler)

if __name__ == '__main__':
    start()
