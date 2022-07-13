# from threading import Thread

# from core.mqtt import MqttConsumer
# from core.message import Message
# from .ant_manager import Ant
# import time
# import sys
# import json
# from .heartrate import HeartRate
# from .powermeter import Powermeter
# from .settings import Settings
# from .speed import Speed

# settings = Settings({
#     'hour_record': False,
#     'run_length': 8046,
#     'trap_length': 200,
#     'hr_sensor_id': 0,
#     'speed_sensor_id': 0,
#     'power_sensor_id': 0,
#     'circumference': 1450,
#     'average_power_time': 3
# }, 'ant')
# mqtt: MqttConsumer
# sensors: dict = dict()


# def message_handler(topic, message: bytes):
#     if topic == 'signals':
#         for e in sensors:
#             sensors[e].signal(message)
#         return
#     try:
#         if topic == 'sensors/manager':
#             json_message = json.loads(message)
#             if sensors.__contains__('speed'):
#                 sensors['speed'].time_int = int(json_message['time_int'])
#     except Exception as e:
#         print(e)


# def send_message(message: Message):
#     print(message.text)
#     mqtt.publish_message(message)


# def loop():
#     while True:
#         v = dict()
#         for e in sensors:
#             v.update(sensors[e].export())
#         # # v.update(timer.export())
#         # v.update(hr.export())
#         # v.update(speed.export())
#         # v.update(powermeter.export())
#         print(v)
#         mqtt.publish(json.dumps(v))
#         time.sleep(1)


# def start():
#     n = len(sys.argv)
#     if n < 2:
#         print("Total arguments passed:", n)
#         return
#     print("Mqtt server ip:", sys.argv[1])
#     print('Starting ANT')
#     settings.load()
#     print(settings.values)
#     # sensors['timer'] = Timer()
#     sensors['hr'] = HeartRate(settings)
#     sensors['speed'] = Speed(send_message, settings)
#     sensors['powermeter'] = Powermeter(send_message, settings)
#     worker_thread = Thread(
#         target=loop,
#         daemon=True)
#     worker_thread.start()
#     Ant(send_message, sensors['hr'], sensors['speed'], sensors['powermeter'])


# mqtt = MqttConsumer(sys.argv[1], 1883, 'ant', ['manager'], ['powermeter_calibration', 'reset'],
#                     settings, message_handler)

# if __name__ == '__main__':
#     start()

import asyncio
import json

from .reader import AntReader, Node

# from .settings import Settings
# from core.mqtt import MqttConsumer
# from core.message import Message

from .heartrate import HeartRate
from .powermeter import Powermeter
from .hall import Hall

import core

# global data storage
data = dict()


# def retrieve_settings(abs):
#     flpt = os.path.abspath(abs)
#     with open(flpt, "r") as p:
#         s = json.load(p)
#     return s


# def message_handler(topic, message: bytes):
#     if topic == 'signals':
#         for e in sensors:
#             sensors[e].signal(message)
#     elif topic == 'sensors/manager':
#         try:
#             json_message = json.loads(message)
#             if sensors.__contains__('speed'):
#                 sensors['speed'].time_int = int(json_message['time_int'])
#         except Exception as e:
#             print(e)


# def send_message(mqtt, message: Message):
#     print(message.text)
#     mqtt.publish_message(message)


# def init():
#     settings = Settings({
#          'hour_record': False,
#          'run_length': 8046,
#          'trap_length': 200,
#          'hr_sensor_id': 0,
#          'speed_sensor_id': 0,
#          'power_sensor_id': 0,
#          'circumference': 1450,
#          'average_power_time': 3
#      }, "ant")

#     try:
#         mqtt = MqttConsumer(sys.argv[1], 1883, 'ant', ['manager'], ['powermeter_calibration', 'reset'], settings,
#                             message_handler)
#         print("Mqtt init at: ", sys.argv[1])
#     except IndexError as e:
#         print(e)
#         sys.exit(-1)


#     heart_rate = HeartRate(settings)
#     speed = Speed(send_message, settings)
#     powermeter = Powermeter(send_message, settings)
#     ant = Ant(send_message, heart_rate, speed, powermeter)

#     # Todo: the dictionary contains the data and not the instances of the classes
#     sensors['heart_rate'] = heart_rate
#     sensors['speed'] = speed
#     sensors['powermeter'] = powermeter

#     settings.load()


async def read_data(sensor):
    while True:
        data.update(sensor.read_data())

        await asyncio.sleep(0.1)


async def mqtt():
    pass


async def main(node):
    # TODO: vedere se si può usare la `with` con Node
    # ant Node
    node.set_network_key(0x00, AntReader.NETWORK_KEY)

    # TODO: ricavare gli id dal database di configurazione
    id_hall = 0
    id_hr = 0
    id_pm = 0

    # sensors
    hall = Hall(node, id_hall)
    hr = HeartRate(node, id_hr)
    pm = Powermeter(node, id_pm)

    # start ant communication and data read
    node.start()

    # release async tasks
    await asyncio.gather(
        read_data(hall),
        read_data(hr),
        read_data(pm),
        mqtt(),
    )

    # close on exit
    node.stop()


def entry_point():
    # `Node` class releases a thread so must be
    # initialized outside the async eventloop

    ant_node = None
    while not ant_node:
        import time
        from .ant.base.driver import DriverNotFound

        try:
            ant_node = Node()
        except DriverNotFound:
            core.log.err("USB not connected")
            time.sleep(1)

    core.log.info("Success on init ant node")

    asyncio.run(main(ant_node))


if __name__ == "__main__":
    entry_point()
