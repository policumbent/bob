import time
import json

from .bikeData import BikeData
from .settings import Settings
from .mqtt import MqttRemote
from .newBt import NewBt
from .message import Message
from .alert import Alert


data = dict()
bt: NewBt
settings: Settings
mqtt: MqttRemote


def send_alert(alert: Alert):
    pass


def handle_settings(s: dict):
    print(s)


def publish_new_settings(s: dict):
    mqtt.publish_new_settings(s)


def send_signal(signal: str):
    mqtt.publish_signal(signal)


def send_message(message: Message):
    pass


# todo: gestire tutte le eccezioni nella serializzazione
#  e deserializzazione
def message_handler(topic, message):
    if topic == 'signals':
        bt.send_signal(message)
        print('signal: ', message)
    if topic[0:9] == 'settings/':
        global settings
        data[topic] = json.loads(message)
        bt.update_settings(data)
        print(json.dumps(data, indent=4))


def start():
    print('Starting Communication')
    global settings
    settings = Settings({})
    # settings.load()
    global mqtt
    # si iscrive al gps per sapere l'ora e la velocità e all'ant per la velocità
    # se il veicolo si sta muovendo le modifiche alle impostazioni verranno rifiutate
    mqtt = MqttRemote('127.0.0.1', 1883, 'new_bt', ['ant', 'gps'], settings, message_handler)
    mqtt.publish_settings(settings)
    global bt
    bt = NewBt({}, 'ciaomarta!', publish_new_settings, send_signal, send_message, send_alert)
    while True:
        bt.handle()


if __name__ == '__main__':
    start()
