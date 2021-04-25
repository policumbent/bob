import time
import json

from .bikeData import BikeData
from .settings import Settings
from .mqtt import MqttRemote
from .taurusBluetooth import TaurusBluetooth
from .message import Message
from .alert import Alert

data = dict()
bt: TaurusBluetooth
settings: Settings
mqtt: MqttRemote


def send_alert(alert: Alert):
    pass


def signal_handler(signal):
    pass
    # if signal == 'settings_updated':
    #     bt.update_settings(settings)


def handle_settings(s: dict):
    print(s)


def send_settings(s: dict):
    mqtt.publish_new_settings(s)


def send_signal(signal: str):
    mqtt.publish_signal(signal)


def send_message(message: Message):
    pass


# todo: gestire tutte le eccezioni nella serializzazione
#  e deserializzazione
def message_handler(topic, message):
    if topic[0:9] == 'settings/':
        data[topic] = json.loads(message)
        all_settings = flat_map(data)
        print(json.dumps(data, indent=4))
        bt.update_settings(all_settings)
        mqtt.publish(json.dumps(all_settings))
        return


def flat_map(d: dict):
    v = dict()
    for e in d:
        v.update(d[e])
    return v


def start():
    print('Starting Communication')
    global settings
    settings = Settings({})
    # settings.load()
    global mqtt
    mqtt = MqttRemote('127.0.0.1', 1883, 'bt', ['ant', 'gps'], [], settings, message_handler)
    mqtt.publish_settings(settings)
    global bt
    bt = TaurusBluetooth({}, send_settings, send_signal, send_message, send_alert)
    while True:
        bt.handle()


if __name__ == '__main__':
    start()
