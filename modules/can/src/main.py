import os, sys
import subprocess
import logging

import threading
from threading import Thread

from datetime import datetime
import time

import can
import cantools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib')))
from pipe import Pipe

from database import Database
import log

home_path = os.getenv("HOME")
db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

FIFO_TO_VIDEO = "fifo_to_video"
FIFO_TO_CAN   = "fifo_to_can"

# complete list of topics
topics = [
    "ant/power",
    "ant/cadence"
    "ant/speed",
    "ant/distance",
    "ant/heartrate",
    "gb/gear",
    "gb/error_code",
    "greta/shifting",
    "greta/rx_timeout",
    "telekhambion/battery"
]

subscribed_topics = [
    "ant/power",
    "ant/cadence"
    "ant/speed",
    "ant/distance",
    "ant/heartrate",
]

# map between Mqtt message and encapsulating message on CAN
topic_to_dbc = {
    "ant/power":        ("BobSrmPower", "SrmPower"),
    "ant/cadence":      ("BobSrmCadence", "SrmCadence"),
    "ant/speed":        ("BobHsSpeed", "HsSpeed"),
    "ant/distance":     ("BobHsDisplacement", "HsDisplacement"),
    "ant/heartrate":    ("BobHR", "HeartRate"),
    "gb/gear":          ("GbData", "GbGear")
}

dbc_to_topic = {
    "GretaError": {         # Meassage sent via CAN
        "TimeOutError": {   # Signal
            "pipe": None,   # Topic where it is published (None -> not published
        }
    },
    "GbError": {
        "GbErrCode": {
            "pipe": None
        },
        "GbGear": {
            "pipe": None
        }
    },
    "GretaData":{
        "TelekBattery": {
            "pipe": None
        },
        "RxShifting": {
            "pipe": None
        },
    },
    "GbData": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GbGear": {
            "pipe": "gb/gear"
        }
    },
    "MiriamGpsData": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GpsSpeed": {
            "pipe": None
        },
        "GpsDisplacement": {
            "pipe": None
        }
    },
    "MiriamGpsCoords": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GpsLatitude": {
            "pipe": None
        },
        "GpsLongitude": {
            "pipe": None
        }
    },
    "MiriamAirQuality": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "CO2Level": {
            "pipe": None
        },
        "TVOC": {
            "pipe": None
        }
    },
    "MiriamTemp": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "Temperature": {
            "pipe": None
        }
    },
    "MiriamGpsOther": {
        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "Altitude": {
            "pipe": None
        }
    }
}

data = dict()

sensors = subscribed_topics

dbc = cantools.database.load_file('./policanbent.dbc')

bus = can.Bus(
        interface='socketcan',
        channel='can0',
        bitrate=500000,
        receive_own_messages=False
    )


def can_logger():
    subprocess.call("./can_logger.sh")     


# Subscribe this module to the MQTT topics specified in the `sensors` list and
# collects their data, putting them in the `data` dictionary

# writes message on bus

def fifo_rx():
    pipe_rx = Pipe(f'{home_path}/bob/{FIFO_TO_CAN}', 'r')

    while True:
        try:
            if pipe_rx.read():
                for rd in pipe_rx.get_data().rstrip().split("-"):
                    if rd != "":
                        sensor, value = rd.split(":")

                        id_name = topic_to_dbc[sensor][0]
                        sig_name = topic_to_dbc[sensor][1]

                        pl = dbc.encode_message(id_name, {sig_name: value})
                        id_frame = dbc.get_message_by_name[id_name].frame_id
                        can_frame = can.Message(arbitration_id=id_frame, data=pl)

                        try:
                            bus.send(can_frame)
                        except can.CanError as e:
                            log.err(f"CAN: {e}")

        except Exception as e:
            log.err(f"FIFO: {e}")
        #finally:
            # TODO: consider adding a sleep


def can_reader():
    pipe_to_video = Pipe(f'{home_path}/bob/{FIFO_TO_VIDEO}', 'w')

    while True:
        try:
            for msg in bus:
                decoded_msg = dbc.decode_message(msg.arbitration_id, msg.data)
                msg_name = dbc.get_message_by_frame_id(msg.arbitration_id).name

                row = dict()
                row["timestamp"] = time.time()

                for signal in decoded_msg:
                    if dbc_to_topic[msg_name][signal]["pipe"] != None:
                        pipe_to_video.write(f"{dbc_to_topic[msg_name][signal]['pipe']}:{decoded_msg[signal]}")
                        row[signal] = decoded_msg[signal]
                        
                if("database_instance" in dbc_to_topic[msg_name]):
                    write_db(dbc_to_topic[msg_name]["database_instance"], dbc_to_topic[msg_name]["csv_dump"], row)
                        
        except Exception as e:
            log.err(f"FIFO: {e}")


def write_csv(row, name_file):
    with open(name_file, "a") as csv_file:
        values = ''
        for value in row.values():
            values += f'{value},'
        values = f"{values.rstrip(',')}\n"
        csv_file.write(values)


def write_db(db, name_file: str, row: dict):
    logging.debug("attempting to write on dB")
    try:
        write_csv(row, name_file)
    except Exception as e:
        log.err(e)
        logging.error(f"CSV EXCEPTION: {e}")
    try:
        db.insert_data(row)
    except Exception as e:
        log.err(e)
        logging.error(f"DATABASE EXCEPTION: {e}")


def main():
    ## Database gathering
    # create database object to interact with the tables
    #########################################################################################################
    dbc_to_topic["GbData"]["database_instance"] = Database(table="gear", path=db_path, max_pending=0)
    dbc_to_topic["MiriamGpsData"]["database_instance"] = Database(table="gps_data", path=db_path, max_pending=0)
    dbc_to_topic["MiriamGpsCoords"]["database_instance"] = Database(table="gps_coordinates", path=db_path, max_pending=0)
    dbc_to_topic["MiriamAirQuality"]["database_instance"] = Database(table="air_quality", path=db_path, max_pending=0)
    dbc_to_topic["MiriamTemp"]["database_instance"] = Database(table="internal_temperature", path=db_path, max_pending=0)
    dbc_to_topic["MiriamGpsOther"]["database_instance"] = Database(table="gps_altitude", path=db_path, max_pending=0)
    #########################################################################################################

    can_logger_thread = Thread(target=can_logger)
    can_logger_thread.start()

    can_reader_thread = Thread(target=can_reader)
    fifo_rx_thread    = Thread(target=fifo_rx)

    while True:
        if not can_reader_thread.is_alive():
            can_reader_thread.start()
        
        if not fifo_rx_thread.is_alive():
            fifo_rx_thread.start()

        time.sleep(1)


if __name__ == '__main__':
    main()