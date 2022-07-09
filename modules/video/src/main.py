import asyncio

from asyncio import sleep
from .camera import Camera, OverlayElement
from .colors import Colors
from core import log

data = {"speed": 40, "power": 55}

async def video():
    # main loop of the camera logic
    while True:
        try:
            with Camera() as vcam:
                vcam.with_grid()
                vcam.with_zoom(0)
                vcam.with_overlay_data(data)

                vcam.add_overlay_element(OverlayElement((0, 0), Colors.red, "power"))
                vcam.add_overlay_element(OverlayElement((1, 1), Colors.green, "speed"))

                await vcam.start_with_overlay()
        except Exception:
            log.err("Camera is not enabled")
            await sleep(1)


async def mqtt():
    global data

    while True:
        try:
            data["power"] += 10
            data["speed"] += 100

            await sleep(0.5)
        except:
            pass


async def main():
    # release async tasks
    await asyncio.gather(video(), mqtt())


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()
