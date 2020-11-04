import time
import json
from .settings import Settings
from .mqtt import MqttConsumer
from .message import Message
from .alert import Alert
from .raspy_sensors import RaspySensors
from .timer import Timer

settings = Settings({
    'max_temp': 70,
    'autopause': True,
    'bike': 'taurusx'
})
mqtt: MqttConsumer
timer = Timer()
speed_0 = 0.1


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)

# todo: opzione per scegliere quale sensore usare per l'autopausa


def handle_speed(speed: float):
    global speed_0
    if speed_0 > 0.0 and speed == 0 and settings.autopause:
        timer.autopause()
    elif speed_0 == 0.0 and speed > 0.0:
        timer.autostart()
    speed_0 = speed


def message_handler(topic, message):
    if topic == 'sensors/ant':
        json_message = json.loads(message)
        handle_speed(json_message['speed'])
        print('ant', json_message['speed'])

    if topic == 'sensors/gps':
        json_message = json.loads(message)
        print('gps', json_message['speedGPS'])


def new_settings_handler(s):
    pass


def start():
    print('Starting Communication')
    settings.load()
    global mqtt
    mqtt = MqttConsumer('192.168.1.20', 1883, 'manager', ['ant', 'gps'],
                        settings, message_handler, new_settings_handler)
    sensors = RaspySensors(send_message, send_alert, settings)
    while True:
        v = dict()
        v.update(sensors.export())
        v.update(timer.export())
        v.update({'bike': settings.bike})
        # print(data)
        mqtt.publish(json.dumps(v))
        time.sleep(1)


if __name__ == '__main__':
    start()
