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
logging.basicConfig(filename='error_messages.log', filemode="w", level=logging.DEBUG)

# global data storage

data = {
    "powermeter": {
        "valid": False,
        "database_instance": None, # table where to publish data
        "database_buffer": list(), # a list of rows that must be published in the database
        "csv_dump": "",            # file where it saves information
        "payload": {
            "timestamp": 0,
            "power": 0,
            "instant_power": 0,
            "cadence": 0
        }
    },
    "hall": {
        "valid": False,
        "database_instance": None,
        "database_buffer": list(),
        "csv_dump": "",
        "payload": {
            "timestamp": 0,
            "hall_cadence": 0,  # not currently supported by our hall sensor
            "speed": 0,
            "distance": 0
        }                     
    },
    "heartrate": {
        "valid": False,
        "database_instance": None,
        "database_buffer": list(),
        "csv_dump": "",
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
            logging.debug(f"Data read with payload {data}")

            write_db(data[sensor.get_sensor_type()]["database_instance"], data[sensor.get_sensor_type()]["csv_dump"], sensor.get_sensor_type())

        else:
            data[sensor.get_sensor_type()]["valid"] = False
        await asyncio.sleep(1)


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
            logging.error(f"MQTT EXCEPTION: {e}")
        finally:
            await asyncio.sleep(1)


def write_csv(row, name_file):
    with open(name_file, "a") as csv_file:
        values = ''
        for value in row.values():
            values += f'{value},'
        values = f"{values.rstrip(',')}\n"
        csv_file.write(values)


def write_db(db, name_file: str, sensor_type: str):
    logging.debug("attempting to write on dB")
    if(data[sensor_type]["valid"] == True):

        row = data[sensor_type]["payload"].copy()
        data[sensor_type]["database_buffer"].append(row)
        logging.debug(f"attempt succeeded with {row}")

        try:
            write_csv(row, name_file)
        except Exception as e:
            log.err(e)
            logging.error(f"CSV EXCEPTION: {e}")
        try:
            for r in data[sensor_type]["database_buffer"].copy(): 
                db.insert_data(r)
                data[sensor_type]["database_buffer"].remove(r)
        except Exception as e:
            log.err(e)
            logging.error(f"DATABASE EXCEPTION: {e} --> {data[sensor_type]['database_buffer']}")
    
    else:
        logging.debug(f"attempt failed --> {data[sensor_type]}")



async def main():
    # retrive configurations from db
    home_path = os.getenv("HOME")
    db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

    # generate csv name for the run and import keys to the csv file
    data["powermeter"]["csv_dump"] = f"{home_path}/bob/csv/powermeter_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
    with open(data["powermeter"]["csv_dump"], "w") as csv_file:
        csv_file.write(f'{",".join(data["powermeter"]["payload"].keys())}\n')

    data["hall"]["csv_dump"] = f"{home_path}/bob/csv/hall_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
    with open(data["hall"]["csv_dump"], "w") as csv_file:
        csv_file.write(f'{",".join(data["hall"]["payload"].keys())}\n')

    data["heartrate"]["csv_dump"] = f"{home_path}/bob/csv/hearthrate_{strftime('%d-%m-%Y@%H:%M:%S')}.csv"
    with open(data["heartrate"]["csv_dump"], "w") as csv_file:
        csv_file.write(f'{",".join(data["heartrate"]["payload"].keys())}\n')

    # create database object to interact with the tables
    data["powermeter"]["database_instance"] = Database(table="powermeter", path=db_path, max_pending=0)
    data["hall"]["database_instance"] = Database(table="hall", path=db_path, max_pending=0)
    data["heartrate"]["database_instance"] = Database(table="heartrate", path=db_path, max_pending=0)


    config = Database(path=db_path).config("ant")

    bike = "taurusx" # TODO: modify the database config -- not working on Cerberus, only on Phoenix
    
    hall_id = config.get(bike).get("hall_id")
    hall_type = config.get(bike).get("hall_type")
    hr_id = config.get(bike).get("hr_id")
    pm_id = config.get(bike).get("pm_id")


    logging.debug("Configuration successfully retrieved")
    try:
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
            )

    except DriverNotFound:
        log.err("USB not connected")
        logging.error("USB not connected")
    except Exception as e:
        log.err(e)
        logging.error(f"MAIN EXCEPTION: {e}")
    finally:
        await asyncio.sleep(1)


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
