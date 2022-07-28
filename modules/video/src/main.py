import asyncio
import os

from asyncio import sleep
from .camera import Camera, OverlayElement, CameraError
from .colors import Colors

from core import log, Mqtt, Database
from core.mqtt import Message


# global data storage
data = dict()

# mqtt sensors to read
sensors = ["ant/speed", "ant/cadence", "ant/power", "ant/heartrate", "gear"]


async def video():
    # main loop of the camera logic

    db_path = os.getenv("DATABASE_PATH") or "~/bob/database.db"
    config = Database(path=db_path).config("video")
    
    while True:
        try:
            with Camera() as vcam:
                log.info("Camera is running")

                vcam.with_grid(config.get("grid") or False)
                vcam.with_zoom(config.get("zoom") or 0)

                # data overlay
                vcam.with_overlay_data(data)

                vcam.add_overlay_element(
                    OverlayElement((0, 0), Colors.black, "ant/speed")
                )
                vcam.add_overlay_element(
                    OverlayElement((4, 0), Colors.blue, "ant/power")
                )
                vcam.add_overlay_element(
                    OverlayElement((0, 3), Colors.red, "ant/heartrate")
                )
                vcam.add_overlay_element(
                    OverlayElement((4, 3), Colors.white, "ant/cadence")
                )
                vcam.add_overlay_element(OverlayElement((2, 3), Colors.white, "gear"))

                await vcam.start_with_overlay()

        except CameraError:
            log.err("Camera is not enabled")
        except Exception as e:
            log.err(e)
        finally:
            await sleep(1)


async def mqtt():
    while True:
        try:
            # will connect to the mosquitto server broker on the local docker

            async with Mqtt() as client:
                message_loop = await client.sensor_subscribe(sensors)
                async with message_loop as messages:
                    async for msg in messages:
                        msg = Message(msg)

                        data.update({msg.sensor: msg.value})
        except Exception as e:
            log.err(f"MQTT: {e}")
        finally:
            await sleep(1)


async def main():
    # release async tasks
    await asyncio.gather(video(), mqtt())


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
