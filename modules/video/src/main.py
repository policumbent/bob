import asyncio
import os

from asyncio import sleep
from .camera import Camera, OverlayElement, CameraError
from .colors import Colors

from core import log, Mqtt, Database, time
from core.mqtt import Message


# global data storage
data = dict()

# mqtt sensors to read
sensors = ["ant/speed", "ant/distance", "ant/power", "ant/heartrate", "gear"]


async def video(config):
    # main loop of the camera logic
    while True:
        try:
            with Camera() as vcam:
                log.info("Camera is running")

                vcam.with_grid(config.get("grid") or False)
                vcam.with_zoom(config.get("zoom") or 0)
                vcam.with_recording(
                    config.get("recording") or False,
                    path=config.get("recording_path") or "/home/pi/bob/onboard_video",
                    filename=time.human_timestamp()[:-4],
                )

                # data overlay
                vcam.with_overlay_data(data)

                vcam.add_overlay_element(
                    OverlayElement((0, 0), Colors.black, sensors[0])
                )
                vcam.add_overlay_element(
                    OverlayElement((4, 3), Colors.white, sensors[1])
                )
                vcam.add_overlay_element(
                    OverlayElement((4, 0), Colors.blue, sensors[2])
                )
                vcam.add_overlay_element(OverlayElement((0, 3), Colors.red, sensors[3]))
                vcam.add_overlay_element(
                    OverlayElement((2, 3), Colors.white, sensors[4])
                )

                await vcam.start_with_overlay()

        except CameraError:
            log.err("Camera is not enabled")
        except Exception as e:
            log.err(e)
        finally:
            await sleep(1)


async def mqtt(_):
    while True:
        try:
            # will connect to the mosquitto server broker on the local docker
            async with Mqtt() as client:
                message_loop = await client.sensor_subscribe(sensors)
                async with message_loop as messages:
                    async for msg in messages:
                        msg = Message(msg)

                        data.update({msg.sensor: round(msg.value)})
        except Exception as e:
            log.err(f"MQTT: {e}")
        finally:
            await sleep(1)


async def main():
    # retrive configurations from db
    home_path = os.getenv("HOME")
    db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

    config = Database(path=db_path).config("video")

    # release async tasks
    await asyncio.gather(video(config), mqtt(config))


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
