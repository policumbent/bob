import sys
from time import sleep, time
import json
from .settings import Settings
from .common_files.mqtt import MqttRemote
from .common_files.alert import Alert
from .common_files.message import Message
from .pyxbee_v3 import PyxbeeV3
from .common_files.bikeData import BikeData

mqtt: MqttRemote
pyxbee_v3: PyxbeeV3
bike_data: BikeData


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    try:
        if topic == 'sensors/manager':
            manager_dict: dict = json.loads(message)
            bike_data.set_manager(manager_dict)
        if topic == 'sensors/ant':
            ant_dict: dict = json.loads(message)
            bike_data.set_ant(ant_dict)
        if topic == 'sensors/gps':
            gps_dict: dict = json.loads(message)
            bike_data.set_gps(gps_dict)
        if topic == 'sensors/hall_sensor':
            hall_sensor_dict: dict = json.loads(message)
            bike_data.set_hall_sensor(hall_sensor_dict)
        if topic == 'sensors/gear':
            gear_dict: dict = json.loads(message)
            bike_data.set_gear(gear_dict)
        if topic == 'sensors/accelerometer':
            accelerometer_dict: dict = json.loads(message)
            bike_data.set_accelerometer(accelerometer_dict)
        if topic == 'sensors/weather':
            weather_dict: dict = json.loads(message)
            bike_data.set_weather(weather_dict)
    except Exception as e:
        print(e)


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting Pyxbee V3')
    settings = Settings({}, 'pyxbee_v3')
    global pyxbee_v3
    pyxbee_v3 = PyxbeeV3(settings, send_alert, send_message)
    global bike_data
    bike_data = BikeData(['manager', 'ant', 'gps', 'hall_sensor', 'gear', 'accelerometer', 'weather'])
    global mqtt
    mqtt = MqttRemote(sys.argv[1], 1883, 'pyxbee_v3',
                      ['manager', 'ant', 'gps', 'hall_sensor', 'accelerometer', 'gear', 'weather'], [''],
                      settings, message_handler)
    while True:
        message = pyxbee_v3.get_mqtt_data(bike_data)
        mqtt.publish(message)
        # remote_data = pyxbee_v2.get_data()
        # mqtt.publish_data('remote_data', json.dumps(remote_data))
        sleep(1)


if __name__ == '__main__':
    start()