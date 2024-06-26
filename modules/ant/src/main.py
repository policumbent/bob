import threading
from threading import Thread

import json

import logging
import os, sys, stat

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


FIFO_VID = f"{home_path}/bob/{FIFO_TO_VIDEO}"
if os.path.exists(FIFO_VID):
    if not stat.S_ISFIFO(os.stat(FIFO_VID).st_mode):
        os.remove(FIFO_VID)
        os.mkfifo(FIFO_VID)
else:
    os.mkfifo(FIFO_VID)


FIFO_CAN = f"{home_path}/bob/{FIFO_TO_CAN}"
if os.path.exists(FIFO_CAN):
    if not stat.S_ISFIFO(os.stat(FIFO_CAN).st_mode):
        os.remove(FIFO_CAN)
        os.mkfifo(FIFO_CAN)
else:
    os.mkfifo(FIFO_CAN)

# global data storage

data = {
    "powermeter": {
        "valid": False,
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
        "csv_dump": "",
        "payload":{
            "timestamp": 0,
            "heartrate": 0
        }
    }
}


curr_data = {}


def read_data(sensors):
    fifo_vid = open(FIFO_VID, 'wb', 0)
    # fifo_can = open(FIFO_CAN, 'wb', 0)

    while True:
        for sensor in sensors:
            if(sensor[0].is_data_ready()):
                read = sensor[0].read_data()

                curr_data.update(read)

                try:
                    for key, value in curr_data.items():
                        if key != "timestamp":
                            fifo_vid.write(f"{key}:{value}\n".encode())
                            # fifo_can.write(f"{key}:{value}\n".encode())
                except Exception as e:
                    log.err(e)
                    logging.error(f"PIPE EXCEPTION: {e}")

                data[sensor[0].get_sensor_type()]["payload"].update(read)
                data[sensor[0].get_sensor_type()]["valid"] = True
                logging.debug(f"Data read with payload {data}")

                write_csv(data[sensor[0].get_sensor_type()]["csv_dump"], sensor[0].get_sensor_type())

            else:
                data[sensor[0].get_sensor_type()]["valid"] = False

    fifo_vid.close()
    # fifo_can.close()


def write_csv(name_file: str, sensor_type: str):
    logging.debug("attempting to write on csv")
    if(data[sensor_type]["valid"] == True):
        row = data[sensor_type]["payload"].copy()
        logging.debug(f"attempt succeeded with {row}")

        try:
            with open(name_file, "a") as csv_file:
                values = ''
                for value in row.values():
                    values += f'{value},'
                values = f"{values.rstrip(',')}\n"
                csv_file.write(values)
        except Exception as e:
            log.err(e)
            logging.error(f"CSV EXCEPTION: {e}")
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

    logging.debug("Configuration successfully retrieved")

    try:
        with Node(0x00, AntDevice.NETWORK_KEY) as node:
            hall = Hall(
                node,
                sensor_id=hall_id,
                device_type=DeviceTypeID(hall_type),
                circumference = 377 if (bike == "cerberus") else 1450 # cerberus hall is not mounted on the wheel because of rpm limit
            )
            hr = HeartRate(node, sensor_id=hr_id)
            pm = Powermeter(node, sensor_id=pm_id)

            # start ant loop and data read
            threading.Thread(target=node.start, name="ant.easy").start()

            sensors = [(hall, "hall"), (hr, "heartrate"), (pm, "powermeter")]
            read_data_thread = Thread(target=read_data, args=(sensors,))

            while True:
                if not read_data_thread.is_alive():
                    read_data_thread.start()
                
                sleep(1)

    except DriverNotFound:
        log.err("USB not connected")
        logging.error("USB not connected")
    except Exception as e:
        log.err(e)
        logging.error(f"MAIN EXCEPTION: {e}")


if __name__ == "__main__":
    main()
