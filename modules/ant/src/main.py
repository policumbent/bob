import asyncio
import threading
import logging
import os
from time import strftime, time
from collections import deque

from core import log, Mqtt, Database


from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node

from .heartrate import HeartRate
from .hall import Hall
from .powermeter import Powermeter

# disable all logging for the ant library
logging.disable(logging.WARNING)

# global data storage

data = {
    "powermeter": {
        "valid": False,
        "payload": {
            "timestamp": 0,
            "power": 0,
            "cadence": 0
        }
    },
    "hall": {
        "valid": False,
        "payload": {
            "timestamp": 0,
            "hall_cadence": 0,
            "speed": 0,
            "distance": 0
        }                     
    },
    "heartrate": {
        "valid": False,
        "payload":{
            "timestamp": 0,
            "heartrate": 0
        }
    }
}


mqtt_data = {}


async def read_data(sensor):
    while True:

        if(sensor.is_data_ready()):
            read = sensor.read_data()
            mqtt_data.update(read)
            data[sensor.get_sensor_type()]["payload"].update(read)
            data[sensor.get_sensor_type()]["valid"] = True
        else:
            data[sensor.get_sensor_type()]["valid"] = False

        await asyncio.sleep(0.4)


async def mqtt():
    while True:
        try:
            async with Mqtt() as client:
                while True:
                    for key, value in mqtt_data.items():
                        if key != "timestamp":
                            await client.sensor_publish(f"ant/{key}", value)
                    await asyncio.sleep(0.1)
        except Exception as e:
            log.err(e)
        finally:
            await asyncio.sleep(1)


def write_csv(row, name_file):
    with open(name_file, "a") as csv_file:
        values = ''
        for value in row.values():
            values += f'{value},'
        values = f"{values.rstrip(',')}\n"
        csv_file.write(values)


async def write_db(db, name_file: str, sensor_type: str):
    while True:

        if(data[sensor_type]["valid"] == True):

            row = data[sensor_type]["payload"].copy()

            try:
                write_csv(row, name_file)
            except Exception as e:
                log.err(e)

            try:
                db.insert_data(row)
            except:
                pass
        
        await asyncio.sleep(0.6)


async def main():
    try:
        # retrive configurations from db
        home_path = os.getenv("HOME")
        db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

        # generate csv name for the run and import keys to the csv file
        name_file_powermeter = f"{home_path}/bob/csv/powermeter_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
        with open(name_file_powermeter, "w") as csv_file:
            csv_file.write(f'timestamp,power,cadence\n')

        name_file_hall = f"{home_path}/bob/csv/hall_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
        with open(name_file_hall, "w") as csv_file:
            csv_file.write(f'timestamp,cadence,speed,distance\n')

        name_file_hearthrate = f"{home_path}/bob/csv/hearthrate_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
        with open(name_file_hearthrate, "w") as csv_file:
            csv_file.write(f'timestamp,hearthrate\n')

        # create database object to interact with the tables
        db_powermeter = Database(table="powermeter", path=db_path, max_pending=10)
        db_hall = Database(table="hall", path=db_path, max_pending=10)
        db_hearthrate = Database(table="heartrate", path=db_path, max_pending=10)

        config = Database(path=db_path).config("ant")

        bike = "taurusx"
        
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
                write_db(db_powermeter, name_file_powermeter, "powermeter"),
                write_db(db_hall, name_file_hall, "hall"),
                write_db(db_hearthrate, name_file_hearthrate, "heartrate"),
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
