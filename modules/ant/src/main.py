import asyncio
import threading
import logging
import os

from core import log, Mqtt, Database, time


from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node

from .heartrate import HeartRate
from .hall import Hall
from .powermeter import Powermeter

# disable all logging for the ant library
logging.disable(logging.WARNING)

# global data storage
data = dict()


async def read_data(sensor):
    while True:
        data.update(sensor.read_data())

        await asyncio.sleep(0.05)


async def mqtt():
    while True:
        try:
            async with Mqtt() as client:
                while True:
                    for key, value in data.items():
                        await client.sensor_publish(f"ant/{key}", value)
                    await asyncio.sleep(0.1)
        except Exception as e:
            log.err(e)
        finally:
            await asyncio.sleep(1)


async def write_db(db):
    row = {
        "timestamp": str(0),
        "speed": 0,
        "distance": 0,
        "cadence": 0,
        "hall_cadence": 0,
        "power": 0,
        "heartrate": 0,
    }

    while True:
        row.update({"timestamp": time.human_timestamp(), **data})

        try:
            db.insert_data(row)
        except:
            pass
        
        await asyncio.sleep(1)


async def main():
    while True:
        try:
            # retrive configurations from db
            home_path = os.getenv("HOME")
            db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

            db = Database(table="ant", path=db_path, max_pending=10)
            config = db.config("ant")

            bike = config.get("name")
            
            hall_id = config.get(bike).get("hall_id")
            hall_type = config.get(bike).get("hall_type")
            hr_id = config.get(bike).get("hr_id")
            pm_id = config.get(bike).get("pm_id")

            with Node(0x00, AntDevice.NETWORK_KEY) as node:
                hall = Hall(
                    node,
                    sensor_id=hall_id,
                    device_type=DeviceTypeID(hall_type),
                )
                hr = HeartRate(node, sensor_id=hr_id)
                pm = Powermeter(node, sensor_id=pm_id)

                # start ant loop and data read
                threading.Thread(target=node.start, name="ant.easy").start()

                # release async tasks
                await asyncio.gather(
                    read_data(hall),
                    read_data(hr),
                    read_data(pm),
                    mqtt(),
                    write_db(db),
                )
        except DriverNotFound:
            log.err("USB not connected")
        except Exception as e:
            log.err(e)
        finally:
            await asyncio.sleep(1)


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
