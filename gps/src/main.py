from .gpsinterface import GpsInterface
import time
import json
from .settings import Settings
from .mqtt import MqttSensor


def message_handler(topic, message):
    pass


def start():
    print('Starting')
    settings = Settings({})
    gps = GpsInterface(settings)
    mqtt = MqttSensor('192.168.1.20', 1883, 'gps',
                      settings, message_handler)
    while True:
        print(gps.export())
        mqtt.publish(json.dumps(gps.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
