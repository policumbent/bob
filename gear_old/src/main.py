import time
import json
import sys
from .settings import Settings
from .common_files.mqtt import MqttConsumer
from .common_files.message import Message
from .common_files.alert import Alert
from .gear import Gear

settings = Settings(
    {"gear": {
             "up_positions_s1": [96, 107, 119, 129, 138, 148, 159, 166, 168, 170, 171],
             "up_positions_s2": [174, 165, 157, 146, 141, 134, 127, 117, 115, 113, 112],
             "down_positions_s1": [96, 107, 119, 129, 138, 148, 159, 164, 168, 168, 171],
             "down_positions_s2": [174, 165, 157, 146, 141, 134, 126, 119, 115, 115, 112]
         }
    }, 'gear'
)
mqtt: MqttConsumer
gear: Gear


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


# todo: possiamo gestire la cambiata anche con dei segnali? => per l'app
def message_handler(topic: str, message: bytes):
    if topic == 'sensors/gpio':
        try:
            # todo: gestire parsing error
            json_message = json.loads(message)
            gear.shift(json_message['message'])
            mqtt.publish(json.dumps(gear.export()))
        except Exception as e:
            send_message(Message('Errore cambiata'))
            print(e)

# def send_pressed(message: int):
#     m = {'message': message}
#     print(message)
#     mqtt.publish(json.dumps(m))


def start():
    n = len(sys.argv)
    if n < 2:
        print("Total arguments passed:", n)
        return
    print("Mqtt server ip:", sys.argv[1])
    print('Starting Gear')
    settings.load()
    global mqtt
    mqtt = MqttConsumer(sys.argv[1], 1883, 'gear', ['gpio'], [], settings, message_handler)
    mqtt.publish_settings(settings)
    global gear
    gear = Gear(send_message, settings)
    while True:
        mqtt.publish(json.dumps(gear.export()))
        time.sleep(1)


if __name__ == '__main__':
    start()
