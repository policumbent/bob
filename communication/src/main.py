import time
import json
import sys

from .bikeData import BikeData
from .alert import Alert
from .settings import Settings
from .mqtt import MqttRemote
from .httpService import HttpService

data = dict()
service: HttpService
settings: Settings
bikeData: BikeData = BikeData(['ant', 'gps', 'manager'])
mqtt: MqttRemote


def get_config():
    config = service.get_config()
    # todo: qualcosa per pubblicare i settings su tutti i sensori
    #  si potrebbe anche scegliere di mantenere una struttura gerarchica
    #  con delle impostazioni per ogni sensore
    print(config)


def send_alert(alert: Alert):
    service.post_alert(alert)


def signal_handler(signal):
    if signal == 'get_config':
        get_config()


# todo: gestire tutte le eccezioni nella serializzazione
#  e deserializzazione
def message_handler(topic, message):
    if topic == 'signal':
        signal_handler(message)
        return
    if topic[0:9] == 'settings/':
        data[topic] = json.loads(message)
        all_settings = flat_map(data)
        mqtt.publish(json.dumps(all_settings))
        return
    message = json.loads(message)
    if topic == 'alerts':
        send_alert(message)
    if topic == 'sensors/manager':
        settings.bike = message['bike']
        bikeData.set_manager(message)
    if topic == 'sensors/gps':
        bikeData.set_gps(message)


def new_settings_handler(s):
    pass


def flat_map(d: dict):
    v = dict()
    for e in d:
        v.update(d[e])
    return v


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting Communication')
    global settings
    settings = Settings({
        'server_ip': '192.168.1.20',
        'cert': './cert.crt',
        'server_port': 8080,
        'protocol': 'http',
        'username': 'admin',
        'password': 'admin'
    })
    settings.load()
    global mqtt
    mqtt = MqttRemote(sys.argv[1], 1883, 'http_service',
                      ['ant', 'gps'], settings, message_handler)
    mqtt.publish_settings(settings)
    global service
    service = HttpService(settings)
    while True:
        try:
            service.add_bike_data(json.loads(bikeData.to_json()))
        except Exception as e:
            print(e)
        time.sleep(1)


if __name__ == '__main__':
    start()
