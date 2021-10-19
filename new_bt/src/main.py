import time
import json
import ast

from .common_files.bikeData import BikeData
from .settings import Settings
from .common_files.mqtt import MqttRemote
from .newBt import NewBt
from .common_files.message import Message
from .common_files.alert import Alert


data: dict = dict()
signals_set: set = set()
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
def message_handler(topic, message: bytes):
    if topic == 'signals':
        print('mh signal', message)
        bt.send_signal(message.decode('utf-8'))
    elif topic[0:13] == 'signals_list/':
        signals_list = ast.literal_eval(message.decode('utf-8'))
        for i in signals_list:
            signals_set.add(i)
        bt.update_signals(signals_set)
    # elif topic == 'settings/gear':
    #     return
    elif topic[0:9] == 'settings/':
        global settings
        data[topic] = json.loads(message)
        bt.update_settings(data)
        # print(json.dumps(data, indent=4))


def start():
    print('Starting Communication')
    global settings
    settings = Settings({}, 'new_bt')
    # settings.load()
    global mqtt
    # si iscrive al gps per sapere l'ora e la velocità e all'ant per la velocità
    # se il veicolo si sta muovendo le modifiche alle impostazioni verranno rifiutate
    global bt
    bt = NewBt({}, set(), 'addiomarta!', publish_new_settings, send_signal, send_message, send_alert)
    mqtt = MqttRemote('127.0.0.1', 1883, 'new_bt', [], [], settings, message_handler)
    mqtt.publish_settings(settings)

    while True:
        bt.handle()


if __name__ == '__main__':
    start()
