import asyncio
import threading
import logging
import os
from time import strftime, time

from core import log, Mqtt, Database


from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node

from .heartrate import HeartRate
from .hall import Hall
from .powermeter import Powermeter

# disable all logging for the ant library
logging.disable(logging.WARNING)

# global data storage
data = []
mqtt_data = {}


async def read_data(sensor):
    while True:
        read = sensor.read_data()

        mqtt_data.update(read)

        already_present = False
        for element in data:
            if element["sensor"] == read["sensor"] and element["timestamp"] == read["timestamp"]:
                already_present = True
            
        if not already_present:
            data.append(read)

        await asyncio.sleep(0.05)


async def mqtt():
    while True:
        try:
            async with Mqtt() as client:
                while True:
                    for key, value in mqtt_data.items():
                        if key != "sensor" and key != "timestamp" and key != "saved":
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

        for element in data:
            if element["sensor"] == sensor_type and not element["saved"]:

                if sensor_type == "powermeter":
                    row = {
                        "timestamp": element["timestamp"],
                        "power": element["power"],
                        "cadence": element["cadence"]
                    }
                elif sensor_type == "hall":
                    row = {
                        "timestamp": element["timestamp"],
                        "cadence": element["hall_cadence"],
                        "speed": element["speed"],
                        "distance": element["distance"]                        
                    }
                else:
                    row = {
                        "timestamp": element["timestamp"],
                        "heartrate": element["heartrate"]
                    }

                try:
                    write_csv(row, name_file)
                except Exception as e:
                    log.err(e)

                try:
                    db.insert_data(row)
                except:
                    pass

                element["saved"] = True
        
        await asyncio.sleep(0.1)


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
