import threading
from threading import Thread

import json

import logging
import os, sys

from time import strftime, time, sleep
from collections import deque

from .ant.base.driver import DriverNotFound
from .device import AntDevice, DeviceTypeID, Node

from .heartrate import HeartRate
from .hall import Hall
from .powermeter import Powermeter

#import lib path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib')))
from log import log
from database import Database
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
curr_data_mutex = 0


def read_data(sensors):
    # create database object to interact with the tables
    for sensor in sensors:
        data[sensor[1]]["database_instance"] = Database(table=sensor[1], path=db_path)

    while True:
        for sensor in sensors:
            if(sensor[0].is_data_ready()):
                read = sensor[0].read_data()

                if not curr_data:
                    curr_data_mutex = 1
                    curr_data.update(read)
                    curr_data_mutex = 0

                data[sensor[0].get_sensor_type()]["payload"].update(read)
                data[sensor[0].get_sensor_type()]["valid"] = True
                logging.debug(f"Data read with payload {data}")

                write_db(data[sensor[0].get_sensor_type()]["database_instance"], data[sensor[0].get_sensor_type()]["csv_dump"], sensor[0].get_sensor_type())

            else:
                data[sensor[0].get_sensor_type()]["valid"] = False


def fifo(pipe_name: str):
    pipe = Pipe(f'{home_path}/bob/{pipe_name}', 'w')

    while True:
        try:
            while True:
                if not curr_data:
                    curr_data_mutex = 1

                    for key, value in curr_data.items():
                        if key != "timestamp":
                            pipe.write(f"{key}:{value}")
                    # TODO: consider adding a sleep

                    curr_data_mutex = 0
                
        except Exception as e:
            log.err(e)
            logging.error(f"PIPE EXCEPTION: {e}")
        #finally:
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

    dict_bikename   = None
    dict_config_ant = None

    try:
        with open(f"{home_path}/bob/config/bikename.json") as file_bikename:
            try:
                dict_bikename = json.load(file_bikename)
            except Exception as json_e:
                print(f"ANT: JSON error: {e}")
    except OSError as os_e:
        print(f"ANT: File opening error: {e}")

    try:
        with open(f"{home_path}/bob/config/ant.json") as file_config_ant:
            try:
                dict_config_ant = json.load(file_config_ant)
            except Exception as json_e:
                print(f"ANT: JSON error: {e}")
    except OSError as os_e:
        print(f"ANT: File opening error: {e}")

    bike      = dict_bikename["name"]
    hall_id   = dict_config_ant[bike]["hall_id"]
    hall_type = dict_config_ant[bike]["hall_type"]
    hr_id     = dict_config_ant[bike]["hr_id"]
    pm_id     = dict_config_ant[bike]["pm_id"]

    #config = Database(path=db_path).config("ant")  ->  use db to retreive data: deprecated

    #bike = config.get("name") # retrieves the informations related to the bike   
    #hall_id = config.get(bike).get("hall_id")
    #hall_type = config.get(bike).get("hall_type")
    #hr_id = config.get(bike).get("hr_id")
    #pm_id = config.get(bike).get("pm_id")

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

            sensors = [(hall, "hall"), (hr, "heartrate"), (pm, "powermeter")]
            read_data_thread = Thread(target=read_data, args=(sensors,))
            
            fifo_to_video_thread  = Thread(target=fifo, args=(FIFO_TO_VIDEO,))
            #fifo_to_can_thread    = Thread(target=fifo, args=(FIFO_TO_CAN,))

            while True:
                if not read_data_thread.is_alive():
                    read_data_thread.start()

                if not fifo_to_video_thread.is_alive():
                    fifo_to_video_thread.start()

                #if not fifo_to_video_thread.is_alive():
                #    fifo_to_can_thread.start()
                
                sleep(1)

    except DriverNotFound:
        log.err("USB not connected")
        logging.error("USB not connected")
    except Exception as e:
        log.err(e)
        logging.error(f"MAIN EXCEPTION: {e}")


if __name__ == "__main__":
    main()
