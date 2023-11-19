import os
import subprocess
import logging

from threading import Thread

from datetime import datetime
import time

import asyncio
from asyncio import sleep

import can
import cantools

from core import Database, log
from core.mqtt import Message
from pipe import Pipe

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
            "mqtt": None,   # Topic where it is published (None -> not published
        }
    },
    "GbError": {

        "GbErrCode": {
            "mqtt": None
        },
        "GbGear": {
            "mqtt": None
        }
    },
    "GretaData":{
        "TelekBattery": {
            "mqtt": None
        },
        "RxShifting": {
            "mqtt": None
        },
    },
    "GbData": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GbGear": {
            "mqtt": "gb/gear"
        }
    },
    "MiriamGpsData": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GpsSpeed": {
            "mqtt": None
        },
        "GpsDisplacement": {
            "mqtt": None
        }
    },
    "MiriamGpsCoords": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "GpsLatitude": {
            "mqtt": None
        },
        "GpsLongitude": {
            "mqtt": None
        }
    },
    "MiriamAirQuality": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "CO2Level": {
            "mqtt": None
        },
        "TVOC": {
            "mqtt": None
        }
    },
    "MiriamTemp": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "Temperature": {
            "mqtt": None
        }
    },
    "MiriamGpsOther": {

        "database_instance": None, # table where to publish data
        "csv_dump": "",            # file where it saves information

        "Altitude": {
            "mqtt": None
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


## Sends init debug messages to verify the state of the CAN bus and makes the
## other devices on the bus activate their communication on the bus
#def debug_init():
#    message = can.Message(
#        arbitration_id=0x0,    
#        is_extended_id=False,
#        is_remote_frame=True,
#        dlc=5
#    )
#
#    try:
#        bus.send(message, timeout=0.1)
#
#    except can.CanError:
#        log.err("CAN: DEBUG_INIT message not sent");        


# Subscribe this module to the MQTT topics specified in the `sensors` list and
# collects their data, putting them in the `data` dictionary

#mette il messaggio su bus

async def fifo_ant(pipe : Pipe):
    while True:
        try:
            if pipe.read():
                for rd in pipe.get_data().rstrip().split("-"):
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
        finally:
            await sleep(1)


async def can_reader(pipe):
    while True:
        try:
            for msg in bus:
                decoded_msg = dbc.decode_message(msg.arbitration_id, msg.data)

                msg_name = dbc.get_message_by_frame_id(msg.arbitration_id).name
                    
                row = dict()

                row["timestamp"] = time.time()

                for signal in decoded_msg:
                    if dbc_to_topic[msg_name][signal]["mqtt"] != None:
                        if msg_name=="GbData" and signal=="GbGear":
                            pipe.write(f"{dbc_to_topic[msg_name][signal]['mqtt']}:{decoded_msg[signal]}")
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

async def main():
    home_path = os.getenv("HOME")
    db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

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
    pipe_video = Pipe(f'{home_path}/bob/can_to_video_pipe.txt', 'w')
    pipe_ant=Pipe(f'{home_path}/bob/ant_to_can_pipe.txt', 'r')
    await asyncio.gather(
        can_reader(pipe_video),
        fifo_ant(pipe_ant)
    )

    #debug_init()


def entry_point():
    asyncio.run(main())


if __name__ == '__main__':
    entry_point()