from picamera import PiCamera

import asyncio
import numpy as np

from asyncio import sleep
from PIL import Image, ImageDraw, ImageFont

DEFAULT_FONT = ImageFont.truetype("assets/FreeSans.ttf", 40)

class Camera(PiCamera):
    def __init__(self):
        super().__init__()

        self._overlay = None
        self._img = None
        self._arr = None
        self._draw = None

        self._set_parameters()
        self._new_frame()

    def __del__(self):
        self.close()

    def _set_parameters(self):
        # video parameters based on bike's lcd screen
        self.resolution = (1024, 768)
        self.framerate = 40
        self.rotation = 180

        self.video_stabilization = True


    def _new_frame(self):
        if self._arr is None:
            # create a void frame of the camera resolution
            frame = Image.new("RGBA", self.resolution)
            # instead of using frame.copy() we create a numpy array
            self._arr = np.asarray(frame)

        # we then build an image from the array
        self._img = Image.fromarray(self._arr)
        self._draw = ImageDraw.Draw(self._img)


    def _new_overlay(self):
        self._overlay = self.add_overlay(self._img.tobytes(), layer=3, alpha=100)

    def start(self):
        self.start_preview()

    async def refresh_screen(self):
        # instead of using `overlay.update(img.tobytes())` which uses up a lot of memory
        # we have found more convenient to destroy and recreate the overlay.
        # to avoid annoying behaviours we create the overlay before destroying it
        prev = self._overlay        

        self._new_overlay()   
        self._new_frame()

        self.remove_overlay(prev)

        # sleep before reiterate
        await sleep(0.5)

    async def write_on_screen(self, position, color, content: str):
        if self._overlay is None:
            self._new_overlay()

        self._draw.text(position, content, color, font=DEFAULT_FONT)
        
