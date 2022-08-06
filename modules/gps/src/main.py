import asyncio
import threading
import logging
import os

from core import log, Mqtt, Database, time

from .gpsinterface import GpsInterface


# global data storage
data = dict()


async def read_data(gps_interface):
    while True:
        data.update(gps_interface.read_data())

        await asyncio.sleep(0.1)


async def mqtt():
    while True:
        try:
            async with Mqtt() as client:
                while True:
                    for key, value in data.items():
                        await client.sensor_publish(f"gps/{key}", value)
                    await asyncio.sleep(0.2)
        except Exception as e:
            log.err(e)
        finally:
            await asyncio.sleep(1)


async def write_db(db):
    curr_row = None
    row = {
        "timestamp": str(0),
        "timestampGPS": str(0),
        "latitude": 0,
        "longitude": 0,
        "altitude": 0,
        "speedGPS": 0,
        "distanceGPS": 0,
        "satellites": 0,
        "distance2timing": 0
    }

    while True:
        try:
            row.update(data)

            if row != curr_row:
                row.update({"timestamp": time.human_timestamp()})
                
                db.insert("gps", list(row.values()))

                curr_row = dict(row)
        except:
            pass
        finally:
            await asyncio.sleep(0.2)


async def main():
    while True:
        try:
            # retrive configurations from db
            home_path = os.getenv("HOME")
            db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

            db = Database(table="gps", path=db_path, max_pending=10)
            config = db.config("gps")

            bike = config.get("name")
            latitude_start = config.get(f"latitude_start")
            longitude_start = config.get(f"longitude_start")
            latitude_end = config.get(f"latitude_end")
            longitude_end = config.get(f"longitude_start")
            serial_port = config.get(f"{bike}_gps_serial")

            gps_interface = GpsInterface(
                latitude_start,
                longitude_start,
                latitude_end,
                longitude_end,
                serial_port
            )

            await asyncio.gather(
                read_data(gps_interface),
                mqtt(),
                write_db(db),
            )
        # todo: exception should be something related to serial port
        except Exception as e:
            print(e)
            await asyncio.sleep(0.5)


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
