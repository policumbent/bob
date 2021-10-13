import sys
from time import sleep
import json
from serial import Serial
from .settings import Settings
from .common_files.mqtt import MqttConsumer
from .common_files.alert import Alert
from .common_files.message import Message
from .example_sensor import ExampleSensor
from .common_files.bikeData import BikeData

mqtt: MqttConsumer
bike_data: BikeData
hall_sensor: ExampleSensor


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def send_message(message: Message):
    mqtt.publish_message(message)


def message_handler(topic: str, message: bytes):
    if topic == 'signals':
        hall_sensor.signal(message.decode())
    try:
        if topic == 'sensors/manager':
            manager_dict: dict = json.loads(message)
            bike_data.set_manager(manager_dict)
        if topic == 'sensors/ant':
            ant_dict: dict = json.loads(message)
            bike_data.set_ant(ant_dict)
        if topic == 'sensors/hall_sensor':
            hall_sensor_dict: dict = json.loads(message)
            bike_data.set_hall_sensor(hall_sensor_dict)
        if topic == 'sensors/messages':
            messages_dict: dict = json.loads(message)
            bike_data.set_messages(messages_dict)
    except Exception as e:
        print(e)


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print('Starting Phoenix')
    settings = Settings({}, 'phoenix')
    serial: Serial = Serial('/dev/ttyAMA1', 115200)
    global bike_data
    bike_data = BikeData(['manager', 'ant', 'hall_sensor', 'messages'])
    global mqtt
    mqtt = MqttConsumer(sys.argv[1], 1883, 'phoenix', ['manager', 'ant', 'hall_sensor', 'messages'],
                        [''], settings, message_handler)
    while True:
        try:
            message = json.dumps(bike_data.to_json())
            serial.write(message.encode('utf-8'))
            print(message)
        except Exception as e:
            print(e)
        sleep(1)


if __name__ == '__main__':
    start()
