import asyncio
import collections
import functools
import operator

import core


from .mpu6050 import mpu6050
from datetime import datetime

import csv

row = dict()
fieldnames = ("acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z")
axis = ("x", "y", "z")


def set_offset(mpu):
    # discard the first 100 value
    for _ in range(100):
        mpu.get_accel_data(g=True)
        mpu.get_gyro_data()

    # calculate mean

    acc_buff = []
    gyr_buff = []

    for _ in range(100):
        acc_buff.append(mpu.get_accel_data(g=True))
        gyr_buff.append(mpu.get_gyro_data())

    acc_buff = dict(functools.reduce(operator.add, map(collections.Counter, acc_buff)))
    offset_acc = {k: round(v / 100, 2) for k, v in acc_buff.items()}

    gyr_buff = dict(functools.reduce(operator.add, map(collections.Counter, gyr_buff)))
    offset_gyr = {k: round(v / 100, 2) for k, v in gyr_buff.items()}

    # check dict integrity
    for ax in axis:
        if not offset_gyr.get(ax):
            offset_gyr.update({ax: 0})

        if not offset_acc.get(ax):
            offset_acc.update({ax: 0})

    return offset_acc, offset_gyr


async def sub_offset(data: dict, offset: dict):
    for ax in axis:
        data[ax] -= offset[ax]

    return data


async def read_acc(mpu, offset):
    global row

    while True:
        data = await sub_offset(mpu.get_accel_data(g=True), offset)

        # round data to the second decimal and insert into the db row
        for i, ax in enumerate(axis):
            row.update({fieldnames[i]: round(float(data[ax]), 2)})

        # sleep for 0.1 ms every clicle
        await asyncio.sleep(0.1 / 1000)


async def read_gyro(mpu, offset):
    global row

    while True:
        data = await sub_offset(mpu.get_gyro_data(), offset)

        # round data to the second decimal and insert into the db row
        for i, ax in enumerate(axis):
            row.update({fieldnames[i + 3]: round(float(data[ax]), 2)})

        # sleep for 0.1 ms every clicle
        await asyncio.sleep(0.1 / 1000)


# TODO: deprecated in favor of sqlite db
async def write_csv():
    localtime = datetime.now().strftime("%H.%M.%S")

    curr_row = None

    with open(f"/home/pi/bob/mpu6050_{localtime}.csv", mode="w", newline="") as file:
        file_wrote = csv.DictWriter(file, fieldnames=fieldnames, dialect="excel")
        file_wrote.writeheader()

        while True:
            if row != curr_row:
                # file_wrote.writerow(row)
                curr_row = dict(row)

                acc_x = row["acc_x"]
                acc_y = row["acc_y"]
                acc_z = row["acc_z"]
                gyr_x = row["gyr_x"]
                gyr_y = row["gyr_y"]
                gyr_z = row["gyr_z"]
                
                print(f"acc_x={acc_x:.2f} acc_y={acc_y:.2f} acc_z={acc_z:.2f} gyr_x={gyr_x:.2f} gyr_y={gyr_y:.2f} gyr_z={gyr_z:.2f}")

            await asyncio.sleep(0.1 / 1000)


async def mqtt():
    pass

async def write_db():
    pass


async def main():
    while True:
        try:
            mpu = mpu6050(0x68)

            core.log.info("Init sensor")

            mpu.set_accel_range(mpu.ACCEL_RANGE_2G)
            mpu.set_gyro_range(mpu.GYRO_RANGE_250DEG)

            off_acc, off_gyr = set_offset(mpu)

            await asyncio.gather(
                read_acc(mpu, off_acc),
                read_gyro(mpu, off_gyr),
                write_csv(),
                mqtt(),
            )
        except OSError:
            core.log.err("Sensor not found")
            await asyncio.sleep(.5)


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
