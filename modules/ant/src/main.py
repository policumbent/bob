import asyncio
import threading

import core

from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node
from .heartrate import HeartRate
from .powermeter import Powermeter
from .hall import Hall


# global data storage
data = dict()


async def read_data(sensor):
    while True:
        s_data = sensor.read_data()
        if s_data:
            data.update(s_data)

        await asyncio.sleep(0.1)


async def mqtt():
    while True:
        if data != dict():
            print(data)

        await asyncio.sleep(0.2)


async def main():
    node = None

    while not node:
        try:
            node = Node(0x00, AntDevice.NETWORK_KEY)
        except DriverNotFound:
            core.log.err("USB not connected")
            await asyncio.sleep(1)

    core.log.info("Init ant node")

    # 'with' statement can be used in the same thread on which the instance of the class was instantiated
    # ant Node

    with node:
        # TODO: ricavare gli id dal database di configurazione

        # hall phoenix
        hall = Hall(node, sensor_id=1, device_type=DeviceTypeID.speed)
        # hall torella
        # hall = Hall(node, sensor_id=13583, device_type=DeviceTypeID.speed_cadence)

        hr = HeartRate(node, sensor_id=2, device_type=DeviceTypeID.heartrate)   # Todo: check id
        pm = Powermeter(node, sensor_id=3, device_type=DeviceTypeID.heartrate)  # Todo: check id

        # start ant loop and data read
        threading.Thread(target=node.start, name="ant.easy").start()

        # release async tasks
        await asyncio.gather(
            read_data(hall),
            read_data(hr),
            read_data(pm),
            mqtt(),
        )


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
