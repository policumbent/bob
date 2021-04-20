import time
import json
import sys

import urllib3

from .bikeData import BikeData
from .alert import Alert
from .settings import Settings
from .mqtt import MqttRemote
from .httpService import HttpService

data = dict()
service: HttpService
settings: Settings
bikeData: BikeData = BikeData(['ant', 'gps', 'manager', 'accelerometer'])
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
    if topic[0:13] == 'signals_list/':
        return
    message = json.loads(message)
    if topic == 'alerts':
        send_alert(message)
    if topic == 'sensors/manager':
        settings.bike = message['bike']
        bikeData.set_manager(message)
    if topic == 'sensors/gps':
        bikeData.set_gps(message)
    if topic == 'sensors/ant':
        bikeData.set_ant(message)
    if topic == 'sensors/accelerometer':
        bikeData.set_accelerometer(message)


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
        'server_ip': 'poliserver.duckdns.org',
        'cert': './cert.crt',
        'server_port': 9002,
        'protocol': 'https',
        'username': 'admin',
        'password': 'admin'
    })
    # todo: riabilitare load dei settings
    # settings.load()
    global mqtt
    mqtt = MqttRemote(sys.argv[1], 1883, 'http_service', ['ant', 'gps', 'accelerometer', 'manager'],
                      [], settings, message_handler)
    mqtt.publish_settings(settings)
    global service
    service = HttpService(settings)
    counter = 0
    while True:
        try:
            # print(json.dumps(bikeData.to_json(), indent=4))
            service.add_bike_data(bikeData.to_json())
            # contsrollo la configurazione ogni minuto
            counter %= 60
            # if counter == 0:
                # print('Get config')
                # todo: ottenere la configurazione
                # service.get_config()
            # ottengo informazioni sul vento ogni 10s
            if counter % 10 == 0:
                print('Get weather data from server')
                # ottengo i dati della stazione meteo dal poli server
                # e li pubblico sull'mqtt server
                weather_data = service.get_weather()
                # print(json.dumps(weather_data))
                mqtt.publish_data('weather_station', json.dumps(weather_data))
        except ConnectionRefusedError or urllib3.exceptions.MaxRetryError as e:
            print(e)
        counter += 1
        time.sleep(1)


if __name__ == '__main__':
    start()
