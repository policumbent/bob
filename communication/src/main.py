import time
import json
from .settings import Settings
from .mqtt import MqttRemote
from .httpService import HttpService

data = dict()


def message_handler(topic, message):
    data[topic] = json.loads(message)


def new_settings_handler(s):
    pass


def flat_map(d: dict):
    v = dict()
    for e in d:
        v.update(d[e])
    return v


def start():
    print('Starting Communication')
    settings = Settings({})
    service = HttpService(settings)
    mqtt = MqttRemote('192.168.1.20', 1883, 'http_service', ['ant', 'gps'], new_settings_handler, message_handler)
    while True:
        print(flat_map(data))
        service.add_bike_data(data)
        mqtt.publish(json.dumps(flat_map(data)))
        time.sleep(1)


if __name__ == '__main__':
    start()
