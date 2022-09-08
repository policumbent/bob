
import asyncio

from core import log, Mqtt

from serial import Serial, SerialException

async def main():
    while True:
        try:
            bt = Serial("/dev/rfcomm0", 115200)

            async with Mqtt() as client:
                while True:
                    value = bt.readline().decode()

                    await client.sensor_publish("gear", value)  

        except SerialException:
            log.err("Unable to connect")
        except Exception as e:
            log.err(e)
        finally:
            await asyncio.sleep(1)


def entry_point():
    asyncio.run(main())


if __name__ == '__main__':
    entry_point()
