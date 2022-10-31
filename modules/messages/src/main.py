import time
import json
import sys
from .settings import Settings
from core.mqtt import MqttMessage
from .messages import Messages
from core.message import Message, MexPriority

settings = Settings({
    'trap_priority': MexPriority.low
}, 'messages')
messages = Messages(settings)


def check_json(json_message: dict):
    # todo: migliore modo per validare json
    return (
        json_message.__contains__('text') and
        json_message.__contains__('message_priority') and
        json_message.__contains__('message_type') and
        json_message.__contains__('message_time') and
        json_message.__contains__('message_timeout')
    )


def message_handler(topic: str, message: bytes):
    if not topic[0:9] == 'messages/':
        return
    print(topic, message)
    json_message = json.loads(message)
    # print(topic, '-', json_message)
    if not check_json(json_message):
        return
    m = Message(
        json_message['text'],
        json_message['message_priority'],
        json_message['message_type'],
        json_message['message_time'],
        json_message['message_timeout']
    )
    global messages
    messages.set(m)


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

    settings.load()
    mqtt = MqttMessage(sys.argv[1], 1883, 'messages', [], settings, message_handler)
    while True:
        data = messages.get_values()
        # print(data)
        mqtt.publish(data)
        time.sleep(1)


if __name__ == '__main__':
    start()
