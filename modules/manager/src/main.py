import time
import sys
import json
from .settings import Settings
from core.mqtt import MqttConsumer
from core.message import Message
from core.alert import Alert
from .raspy_sensors import RaspySensors
from .timer import Timer

settings = Settings({
    'max_temp': 70,
    'autopause': True,
    'bike': 'taurusx',
    'autopause_on_gps': False
}, 'manager')
mqtt: MqttConsumer
timer = Timer()
speed_0 = 0.1


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def handle_speed(speed: float):
    global speed_0
    if speed_0 > 0.0 and speed == 0 and settings.autopause:
        timer.autopause()
    elif speed_0 == 0.0 and speed > 0.0:
        timer.autostart()
    speed_0 = speed


def message_handler(topic, message: bytes):
    try:
        if topic == 'signals':
            if message.decode() == 'reset':
                timer.reset()
                send_message(Message('Reset timer effetuato'))

        if topic == 'sensors/ant':
            json_message = json.loads(message)
            if not settings.autopause_on_gps:
                handle_speed(json_message['speed'])
            # print('ant', json_message['speed'])

        if topic == 'sensors/gps':
            json_message = json.loads(message)
            if settings.autopause_on_gps:
                handle_speed(json_message['speedGPS'])
            # print('gps', json_message['speedGPS'])

    except Exception as e:
        print(e)


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting Manager')
    settings.load()
    global mqtt
    mqtt = MqttConsumer(sys.argv[1], 1883, 'manager', ['ant', 'gps'],
                        ['reset', 'stop'], settings, message_handler)
    sensors = RaspySensors(send_message, send_alert, settings)
    while True:
        v = dict()
        v.update(sensors.export())
        v.update(timer.export())
        v.update({'bike': settings.bike})
        v.update({'activity_number': 0})
        # print(data)
        mqtt.publish(json.dumps(v))
        time.sleep(1)

# todo: activity number => progressive number, incremented at restart and reset


if __name__ == '__main__':
    start()
