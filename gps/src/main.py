import time
import sys
import json
from .settings import Settings
from .common_files.mqtt import MqttSensor
from .gpsinterface import GpsInterface


gps: GpsInterface


def message_handler(topic, message):
    if topic == 'signals':
        gps.signal(message.decode())


def start():
    # total arguments
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting GPS')
    settings = Settings({
        'trap_length': 200,
        'latitude_timing_start': 45.032888,
        'longitude_timing_start': 7.792347,
        'latitude_timing_end': 45.032888,
        'longitude_timing_end': 7.792347
    })
    global gps
    gps = GpsInterface(settings)
    mqtt = MqttSensor(sys.argv[1], 1883, 'gps', ['reset'],
                      settings, message_handler)
    while True:
        print(gps.export())
        mqtt.publish(json.dumps(gps.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
