import time
import json
from .settings import Settings
from core.mqtt import MqttConsumer
from core.message import Message
from .power_speed_target import PowerSpeedTarget
from core.bikeData import BikeData

settings = Settings({
    'speed_power_target_csv': 'test_Vittoria.csv',
}, 'power_speed_target')
bikeData: BikeData = BikeData(
    ['ant', 'gps', 'power_speed_target', 'manager', 'gear', 'messages']
)
mqtt: MqttConsumer
distance = 0


def message_handler(topic, message):
    if topic == 'signals':
        return
    try:
        json_message = json.loads(message)
        if topic == 'sensors/ant':
            bikeData.set_ant(json_message)
        elif topic == 'sensors/power_speed_target':
            bikeData.set_power_speed_target(json_message)
    except Exception as e:
        print(e)


def start():
    print('Starting speed_power_target')
    settings.load()
    mqtt = MqttConsumer('192.168.1.20', 1883, 'speed_power_target', ['ant'], settings, message_handler)
    target: PowerSpeedTarget = PowerSpeedTarget(settings, bikeData)
    while True:
        target.export()
        mqtt.publish()
        time.sleep(1)


if __name__ == '__main__':
    start()
