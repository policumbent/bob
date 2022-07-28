import asyncio

from asyncio import sleep
from .camera import Camera, OverlayElement, CameraError
from .colors import Colors

from core import log, Mqtt
from core.mqtt import Message

# global data storage
data = dict()

# mqtt sensors to read
sensors = ["ant/speed", "ant/cadence", "ant/power", "ant/heartrate", "gear"]


async def video():
    # main loop of the camera logic

    while True:
        try:
            with Camera() as vcam:
                log.info("Camera is running")

                vcam.with_grid()
                vcam.with_zoom(0)
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
    await asyncio.gather(mqtt(), video())


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
