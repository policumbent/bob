import time
import json
import sys
from paho.mqtt.client import Client

from core.alert import Alert
from core.mqtt import MqttRemote
from .settings import Settings


data = dict()
mqtt: MqttRemote
external_mqtt: Client
settings: Settings


def send_alert(alert: Alert):
    pass


def signal_handler(signal):
    pass


# todo: gestire tutte le eccezioni nella serializzazione
#  e deserializzazione
def message_handler(topic: str, message: bytes):
    if topic == 'signal':
        signal_handler(message)
        return
    if topic[0:7] == 'sensors':
        try:
            sensor_dict: dict = json.loads(message)
            for key, value in sensor_dict.items():
                if type(value) != str:
                    external_mqtt.publish(f"bikes/{settings.bike}/sensors/{topic[8:]}/{key}", value)
        except Exception as e:
            print(e)
    if topic[0:8] == 'settings':
        external_mqtt.publish(f"bikes/{settings.bike}/settings/{topic[9:]}", message, retain=True)


def external_message_handler(client, userdata, msg):
    print(msg.topic, ':', msg.message.decode('utf-8'))


def new_settings_handler(s):
    pass


def external_on_connect(client, userdata, flags, rc) -> None:
    print("Connected with result code", str(rc))

    """ Il sensore pubblica un json `{"connected": True}`quando si connette """
    status_topic = 'state/{}'.format(settings.bike)
    client.publish(status_topic, json.dumps({"connected": True}), retain=True)


def start_external_mqtt(ip: str, port: int, username: str, password: str):
    client = Client()
    client.on_connect = external_on_connect
    client.on_message = external_message_handler
    # client.username_pw_set(username='test', password='test')
    client.connect(ip, port, keepalive=60)
    client.loop_start()
    return client


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting External Mqtt ')
    global settings
    settings = Settings({
        'server_ip': 'server.policumbent.it',
        'cert': './cert.crt',
        'server_port': 1883,
        'protocol': 'https',
        'username': 'taurusx',
        'password': 'ciao1234'
    }, 'external_mqtt')
    settings.load()
    global external_mqtt
    external_mqtt = start_external_mqtt('server.policumbent.it', 1883, '', '')

    global mqtt
    mqtt = MqttRemote(sys.argv[1], 1883, 'external_mqtt', ['ant', 'gps', 'accelerometer', 'manager', 'hall_sensor'],
                      [], settings, message_handler)
    mqtt.publish_settings(settings)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    start()
