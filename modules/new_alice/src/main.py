import time
import socketio
from asyncio_mqtt import Client, Message
import asyncio
import json

# from core.alert import Alert
from core.mqtt import Mqtt
# from settings import Settings

data = dict()
# mqtt: Mqtt
external_mqtt: Client
# settings: Settings
sio = socketio.AsyncClient()

async def sio_connect():
    global sio
    await sio.connect(f'ws://localhost:1337')

@sio.event
async def connect():
    print('connected')

@sio.event
async def disconnect():
    print('disconnected')


# def send_alert(alert: Alert):
#     pass


def signal_handler(signal):
    pass


# todo: gestire tutte le eccezioni nella serializzazione
#  e deserializzazione
async def message_handler(message: Message):
    print('A message has been received')
    topic = str(message.topic)
    if topic == 'signal':
        signal_handler(message.payload)
        return
    if topic[0:7] == 'sensors':
        try:
            #TODO inserire filtri per i dati che possono e non possono essere mandati
            await sio.emit('new data', json.dumps({"topic": topic.split("/")[-1], "payload":int(message.payload)}))
            print(f'New message {message.payload} inside {topic}')
        except Exception as e:
            print(e)
    # if topic[0:8] == 'settings':
    #     external_mqtt.publish(f"bikes/{settings.bike}/settings/{topic[9:]}", message, retain=True)

# deprecated
def external_message_handler(client, userdata, msg):
    print(msg.topic, ':', msg.message.decode('utf-8'))


def new_settings_handler(s):
    pass

# deprecated
# def external_on_connect(client, userdata, flags, rc) -> None:
#     print("Connected with result code", str(rc))

#     """ Il sensore pubblica un json `{"connected": True}`quando si connette """
#     status_topic = 'state/{}'.format(settings.bike)
#     client.publish(status_topic, json.dumps({"connected": True}), retain=True)

# deprecated
# def start_external_mqtt(ip: str, port: int, username: str, password: str):
#     client = Client()
#     client.on_connect = external_on_connect
#     client.on_message = external_message_handler
#     # client.username_pw_set(username='test', password='test')
#     client.connect(ip, port, keepalive=60)
#     client.loop_start()
#     return client


async def start():
    # n = len(sys.argv)
    # if n < 2:
    #     print("Total arguments passed:", n)
    #     return
    # starts external mqtt server (deprecated)
    # print("Mqtt server ip:", sys.argv[1])
    # print('Starting External Mqtt ')
    # global settings
    # settings = Settings({
    #     'server_ip': 'server.policumbent.it',
    #     'cert': './cert.crt',
    #     'server_port': 1883,
    #     'protocol': 'https',
    #     'username': 'taurusx',
    #     'password': 'ciao1234'
    # }, 'external_mqtt')
    # settings.load()
    # global external_mqtt
    # external_mqtt = start_external_mqtt('server.policumbent.it', 1883, '', '')

    # global mqtt
    # mqtt = MqttRemote(sys.argv[1], 1883, 'external_mqtt', ['ant', 'gps', 'accelerometer', 'manager', 'hall_sensor'],
    #                   [], settings, message_handler)
    # mqtt.publish_settings(settings)
    # starting internal socketIO channel
        # for t in ['ant', 'gps', 'accelerometer', 'manager', 'hall_sensor']:
        #     await client.subscribe(f'sensors/{t}')
        #     client.on_message = on_message
    await sio_connect()
    async with Client('localhost', port=1883) as client:
        async with client.messages(queue_maxsize=-1) as messages:
            await client.subscribe("sensors/#")
            async for message in messages:
                print(f"{message.topic} + {message.payload}")
                asyncio.gather(message_handler(message)) # non funziona con await e con asyncio.run, con gather si...
    while True:
        time.sleep(1)

if __name__ == '__main__':
    asyncio.run(start())
