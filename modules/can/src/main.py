import os

from datetime import datetime

import asyncio
from asyncio import sleep

import can

from core import Mqtt, Database, log
from core.mqtt import Message

from data_reader import data_read


data = dict()

sensors = [
    "ant/speed",
    "ant/distance",
    "ant/power",
    "ant/heartrate",
    "ant/cadence"
]

#data = [
#    "speed/hall",
#    "distance/hall",
#    "wheel_rpm",
#    "power",
#    "pedal_rpm",
#    "heart_rate"
#]


bus = can.Bus(
        interface='socketcan',
        channel='can0',
        bitrate=500000,
        receive_own_messages=True
    )

data_reader = can.BufferedReader()

can.Notifier(bus, [
    can.Logger(f"{datetime.now().replace(microsecond=0).isoformat()}"),
    data_reader
])


def debug_init():
    message = can.Message(
        arbitration_id=0x0,    
        is_extended_id=False,
        is_remote_frame=True,
        dlc=5
    )

    try:
        bus.send(message, timeout=0.1)

    except can.CanError:
        log.err("CAN: DEBUG_INIT message not sent");        


async def mqtt():
    while True:
        try:
            # will connect to the mosquitto server broker on the local docker
            async with Mqtt() as client:
                message_loop = await client.sensor_subscribe(sensors)

                async with message_loop as messages:
                    async for msg in messages:
                        msg = Message(msg)

                        data.update({msg.sensor: round(msg.value)})

        except Exception as e:
            log.err(f"MQTT: {e}")

        finally:
            await sleep(1)


async def main():
    home_path = os.getenv("HOME")

    await asyncio.gather(
        mqtt(),
        data_read(data_reader)
    )

    debug_init()


def entry_point():
    asyncio.run(main())


if __name__ == '__main__':
    entry_point()