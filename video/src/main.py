import time
import json
from .settings import Settings
from .mqtt import MqttConsumer
from .message import Message
from .alert import Alert
from .video import Video
from common_files.bikeData import BikeData

settings = Settings({
    'video_record': False
})
print(settings.default_color_1)
mqtt: MqttConsumer
bikeData: BikeData = BikeData(
    ['ant', 'gps', 'power_speed_target', 'manager', 'gear']
)


def send_message(message: Message):
    mqtt.publish_message(message)


def send_alert(alert: Alert):
    mqtt.publish_alert(alert)


def message_handler(topic, message):
    if topic == 'signals':
        return
    try:
        json_message = json.loads(message)
        if topic == 'sensors/ant':
            bikeData.set_ant(json_message)
        elif topic == 'sensors/gps':
            bikeData.set_gps(json_message)
        elif topic == 'sensors/power_speed_target':
            bikeData.set_power_speed_target(json_message)
        elif topic == 'sensors/manager':
            bikeData.set_manager(json_message)
        elif topic == 'sensors/gear':
            bikeData.set_gear(json_message)
        elif topic == 'messages':
            bikeData.set_messages(json_message)
    except Exception as e:
        print(e)


def start():
    print('Starting Video')
    settings.load()
    global mqtt
    mqtt = MqttConsumer('127.0.0.1', 1883, 'video',
                        ['ant', 'gps', 'power_speed_target', 'manager', 'gear'],
                        settings, message_handler)
    mqtt.subscribe_messages()
    video = Video(bikeData, settings)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    start()
