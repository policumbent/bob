import asyncio
import os
import sys

from asyncio import sleep
from .camera import Camera, OverlayElement, CameraError
from .colors import Colors

from core import log, Mqtt, Database, time
from core.mqtt import Message

#import lib path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib')))
from pipe import Pipe

# global data storage
data = dict()

# mqtt sensors to read
sensors = [
    "ant/speed",
    "ant/distance",
    "ant/power",
    "ant/heartrate",
    "ant/cadence",
    "gb/gear",
]


async def video(config):
    # main loop of the camera logic
    while True:
        try:

            # configuration params
            
            video = config.get("video_rotation") or 0
            overlay = config.get("overlay_rotation") or video

            grid = config.get("grid") or False
            zoom = config.get("zoom") or 0

            recording = config.get("recording") or False
            recording_path = (
                config.get("recording_path") or "/home/pi/bob/onboard_video"
            )


            with Camera(video_rotation=video, overlay_rotation=overlay) as vcam:
                log.info("Camera is running")

                vcam.with_grid(grid)
                vcam.with_zoom(zoom)
                vcam.with_recording(
                    recording,
                    path=recording_path,
                    filename=time.human_timestamp()[:-4],
                )

                # data overlay
                vcam.with_overlay_data(data)

                # velocità altro a sx
                vcam.add_overlay_element(
                    OverlayElement((0, 0), Colors.blue, sensors[0], "kph")
                )
                
                # distanza basso a dx
                vcam.add_overlay_element(
                    OverlayElement((4, 3), Colors.white, sensors[1], "m")
                )

                # potenza alto a dx
                vcam.add_overlay_element(
                    OverlayElement((4, 0), Colors.blue, sensors[2], "W")
                )

                # battito basso a sx
                vcam.add_overlay_element(OverlayElement((0, 3), Colors.red, sensors[3], "bpm"))

                # cadenza ??
                vcam.add_overlay_element(OverlayElement((4, 2), Colors.green, sensors[4], "rpm"))
                
                # marcia basso centro
                vcam.add_overlay_element(
                    OverlayElement((2, 3), Colors.white, sensors[5])
                )

                await vcam.start_with_overlay()

        except CameraError:
            log.err("Camera is not enabled")
        except Exception as e:
            log.err(e)
        finally:
            await sleep(1)


async def fifo(pipe : Pipe):
    while True:
        try:
            if pipe.read():
                for rd in pipe.get_data().rstrip().split("-"):
                    if rd != "":
                        sensor, value = rd.split(":")
                        data.update({f"ant/{sensor}": round(float(value))})
        except Exception as e:
            log.err(f"FIFO: {e}")
        finally:
            await sleep(1)








async def main():
    # retrive configurations from db
    home_path = os.getenv("HOME")
    db_path = os.getenv("DATABASE_PATH") or f"{home_path}/bob/database.db"

    config = Database(path=db_path).config("video")
    #create pipe

    pipe_ant = Pipe(f'{home_path}/bob/named_pipe.txt', 'r')

    pipe_can = Pipe(f'{home_path}/bob/can_to_video_pipe.txt', 'r')
    # release async tasks
    await asyncio.gather(
        video(config),
        fifo(pipe_ant),
        fifo(pipe_can)
        )


def entry_point():
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()

