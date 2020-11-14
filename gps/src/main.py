import time
import sys
import json
from .settings import Settings
from .mqtt import MqttSensor
from .gpsinterface import GpsInterface


def message_handler(topic, message):
    pass


def start():
    # total arguments
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting GPS')
    settings = Settings({
        'latitude_timing_start': 45.032888,
        'longitude_timing_start': 7.792347,
        'latitude_timing_end': 45.032888,
        'longitude_timing_end': 7.792347
    })
    gps = GpsInterface(settings)
    mqtt = MqttSensor(sys.argv[1], 1883, 'gps',
                      settings, message_handler)
    while True:
        print(gps.export())
        mqtt.publish(json.dumps(gps.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
