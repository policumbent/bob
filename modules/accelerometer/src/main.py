import asyncio
from mpu6050 import mpu6050
from datetime import datetime

import csv
import time

row = None
fieldnames = ("acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z")

async def read_data():
    global row

    mpu = mpu6050(0x68)

    a_first = mpu.get_accel_data(g=True)
    g_first = mpu.get_gyro_data()

    a_off_x = a_first['x']
    a_off_y = a_first['y']
    a_off_z = a_first['z']

    g_off_x = g_first['x']
    g_off_y = g_first['y']
    g_off_z = g_first['z']

    while True:
        acc = mpu.get_accel_data(g=True)
        gyr = mpu.get_gyro_data()

        acc['x'] -= a_off_x
        acc['y'] -= a_off_y
        acc['z'] -= a_off_z

        gyr['x'] -= g_off_x
        gyr['y'] -= g_off_y
        gyr['z'] -= g_off_z

        row = {
            fieldnames[0]: float(round(float(acc['x']),2)),
            fieldnames[1]: round(float(acc['y']),2),
            fieldnames[2]: round(float(acc['z']),2),
            fieldnames[3]: round(float(gyr['x']),2),
            fieldnames[4]: round(float(gyr['y']),2),
            fieldnames[5]: round(float(gyr['z']),2),
        }


        # sleep for 0.1 ms every clicle
        await asyncio.sleep(0.1 / 1000)

async def write_db():
    localtime = datetime.now().strftime("%H.%M.%S")
    print(localtime)
    
    curr_row = None
    with open(f'/home/pi/mpu6050_{localtime}.csv', mode='w', newline="") as file:
        file_wrote = csv.DictWriter(file, fieldnames=fieldnames, dialect='excel')
        file_wrote.writeheader()

        start = time.time()
        while time.time() - start <= 1:
            if row != curr_row:
                file_wrote.writerow(row)
                curr_row = row
                
                await asyncio.sleep(0.1 / 1000)

        


async def mqtt():
    pass


async def main():
    acc_task = asyncio.create_task(read_data())
    db_task = asyncio.create_task(write_db())
    mqtt_task = asyncio.create_task(mqtt())

    await asyncio.wait([acc_task, db_task, mqtt_task])

def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()