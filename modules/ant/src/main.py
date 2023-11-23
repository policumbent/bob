import threading
from threading import Thread

import logging
import os, sys
from time import strftime, time
from collections import deque

from core import log, Database
from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node

from .heartrate import HeartRate
from .hall import Hall
from .powermeter import Powermeter

#import lib path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib')))
from pipe import Pipe

# disable all logging for the ant library
#logging.disable(logging.WARNING)
logging.basicConfig(filename='error_messages.log', filemode="w", level=logging.DEBUG)

# retrive configurations from db
home_path = os.getenv("HOME")
db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

FIFO_TO_VIDEO = "fifo_to_video"
FIFO_TO_CAN   = "fifo_to_can"

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


curr_data = {}


def read_data(sensor):
    while True:
        if(sensor.is_data_ready()):
            read = sensor.read_data()
            curr_data.update(read)
            data[sensor.get_sensor_type()]["payload"].update(read)
            data[sensor.get_sensor_type()]["valid"] = True
            logging.debug(f"Data read with payload {data}")

            write_db(data[sensor.get_sensor_type()]["database_instance"], data[sensor.get_sensor_type()]["csv_dump"], sensor.get_sensor_type())

        else:
            data[sensor.get_sensor_type()]["valid"] = False
        # TODO: consider adding a sleep


# TODO: make it a thread with threading
def fifo(pipe_name: str):
    pipe_to_video = Pipe(f'{home_path}/bob/{pipe_name}', 'w')

    while True:
        try:
            while True:
                for key, value in curr_data.items():
                    if key != "timestamp":
                        pipe.write(f"{key}:{value}")
                # TODO: consider adding a sleep
        except Exception as e:
            log.err(e)
            logging.error(f"PIPE EXCEPTION: {e}")
        finally:
            # TODO: consider adding a sleep


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


def main():
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

    bike = config.get("name") # retrieves the informations related to the bike   
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
                circumference = 1490 * 3.125 if (bike == "cerberus") else 1450 # cerberus hall is not mounted on the wheel because of rpm limit
            )
            hr = HeartRate(node, sensor_id=hr_id)
            pm = Powermeter(node, sensor_id=pm_id)

            # start ant loop and data read
            threading.Thread(target=node.start, name="ant.easy").start()

            read_data_hall_thread = Thread(target=read_data, args=hall)
            read_data_hr_thread   = Thread(target=read_data, args=hr)
            read_data_pm_thread   = Thread(target=read_data, args=pm)
            
            fifo_to_video_thread  = Thread(target=fifo, args=FIFO_TO_VIDEO)
            fifo_to_can_thread  = Thread(target=fifo, args=FIFO_TO_CAN)

            while True:
                if not read_data_hall_thread.is_alive():
                    read_data_hall_thread.start()

                if not read_data_hr_thread.is_alive():
                    read_data_hr_thread.start()

                if not read_data_pm_thread.is_alive():
                    read_data_pm_thread.start()

                if not fifo_to_video_thread.is_alive():
                    fifo_to_video_thread.start()

                if not fifo_to_video_thread.is_alive():
                    fifo_to_can_thread.start()
                
                time.sleep(1)

    except DriverNotFound:
        log.err("USB not connected")
        logging.error("USB not connected")
    except Exception as e:
        log.err(e)
        logging.error(f"MAIN EXCEPTION: {e}")


if __name__ == "__main__":
    main()