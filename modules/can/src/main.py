import os
import subprocess

from threading import Thread

from datetime import datetime
import time

import asyncio
from asyncio import sleep

import can
import cantools

from core import Mqtt, Database, log
from core.mqtt import Message

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

topic_to_dbc = {
    "ant/power":        ("BobSrmPower", "SrmPower"),
    "ant/cadence":      ("BobSrmCadence", "SrmCadence"),
    "ant/speed":        ("BobHsSpeed", "HsSpeed"),
    "ant/distance":     ("BobHsDistance", "HsDistance"),
    "ant/heartrate":    ("BobHR", "HeartRate"),
    "gb/gear":          ("GbData", "GbGear")
}

dbc_to_topic = {
    "GretaError": {
        "TimeOutError": "greta/timeout_error"
    },
    "GbError": {
        "GbErrCode": "gb/error_code",
        "GbGear": "gb/gear"
    },
    "GretaData": {
        "TelekBattery": "telekhambion/battery",
        "RxShifting": "greta/shifting",
    },
    "GbData": {
        "GbGear": "gb/gear"
    }
}

data = dict()

sensors = topics

#sensors = [
#    "speed/hall",
#    "distance/hall",
#    "wheel_rpm",
#    "power",
#    "pedal_rpm",
#    "heart_rate"
#]


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
                        
                        id_name = topic_to_dbc[msg.sensor][0]
                        sig_name = topic_to_dbc[msg.sensor][1]
                        pl = db.encode_message(id_name, {sig_name: msg.value})
                        id_frame = db.get_message_by_name[id_name].frame_id
                        can_frame = can.Message(arbitration_id=id_frame, data=pl)

                        try:
                            bus.send(can_frame)
                        except can.CanError as e:
                            log.err(f"CAN: {e}")


        except Exception as e:
            log.err(f"MQTT: {e}")

        finally:
            await sleep(1)


async def can_reader():
    try:
        async with Mqtt() as client:
            for msg in bus:
                decoded_msg = dbc.decode_message(msg.arbitration_id, msg.data)

                msg_name = dbc.get_message_by_frame_id(msg.arbitration_id).name

                for signal in decoded_msg:
                    await client.sensor_publish(dbc_to_topic[msg_name][signal], decoded_msg[signal])
                    
    except Exception as e:
            log.err(f"MQTT: {e}")


async def main():
    home_path = os.getenv("HOME")

    can_logger_thread = Thread(target=can_logger)
    can_logger_thread.start()

    await asyncio.gather(
        mqtt(),
        can_reader()
    )

    #debug_init()


def entry_point():
    asyncio.run(main())


if __name__ == '__main__':
    entry_point()