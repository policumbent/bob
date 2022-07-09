import operator
import numpy as np

from asyncio import sleep
from picamera import PiCamera
from picamera.exc import PiCameraMMALError as CameraError
from PIL import Image, ImageDraw, ImageFont

from .colors import Colors


class OverlayElement:
    DATA = None

    def __init__(
        self,
        position: tuple,
        color: Colors,
        key_data: str,
        sectors_length: int = 1,
        direction="row",
    ):
        self._position = position
        self._color = color
        self._key_data = key_data
        self._sectors_length = abs(sectors_length)
        self._direction = direction

    def __len__(self):
        return self._sectors_length

    @property
    def position(self):
        return self._position

    @property
    def color(self):
        return self._color

    @property
    def direction(self):
        return self._direction == "row"

    @property
    def data(self):
        if not self.DATA or not isinstance(self.DATA, dict):
            return None

        data = self.DATA[self._key_data]

        return str(data) if data else None

    def is_multiline(self):
        return self._sectors_length > 1

    def to_writable(self):
        return self.position, self.color, self.data


class Camera(PiCamera):
    FONT_PATH = "assets/Inconsolata.ttf"

    def __init__(self, screen_dim=(1024, 760), sectors=(5, 4)):
        super().__init__()

        self._overlay = None
        self._img = None
        self._arr = None
        self._draw = None
        self._grid = None
        self._overlay_element_list = []

        # screen parameters
        self._screen_dim_x, self._screen_dim_y = screen_dim
        self._sectors_x, self._sectors_y = sectors

        # default font for strings overlay
        # size is retrived form the y sector dimension
        self._default_font = ImageFont.truetype(
            self.FONT_PATH,
            self._screen_dim_y // self._sectors_y - 30,
        )

        self._set_parameters()

    def _set_parameters(self):
        # video parameters based on bike's lcd screen
        self.resolution = (self._screen_dim_x, self._screen_dim_y)
        self.framerate = 40
        self.rotation = 180

        self.video_stabilization = True

    def _new_overlay(self):
        self._overlay = self.add_overlay(
            self._img.tobytes(), format="rgba", layer=3, alpha=100
        )

    def _new_frame(self):
        """Create a new blank frame for the overlay"""

        if self._arr is None:
            # create a void frame of the camera resolution
            frame = Image.new("RGBA", self.resolution)
            # instead of using frame.copy() we create a numpy array
            self._arr = np.asarray(frame)

        # we then build an image from the array
        self._img = Image.fromarray(self._arr)
        self._draw = ImageDraw.Draw(self._img)

        if self._grid:
            self._write_grid()

    def _write_grid(self):
        """Write grid and show the sectors"""

        dim_x = self._screen_dim_x
        dim_y = self._screen_dim_y

        sectors_x = self._sectors_x
        sectors_y = self._sectors_y

        # write lines parallel to y
        for i in range(1, sectors_x):
            pos = (dim_x // sectors_x) * i
            self._draw.line((pos, 0, pos, dim_y), width=2, fill="white")

        # write lines parallel to x
        for i in range(1, sectors_y):
            pos = (dim_y // sectors_y) * i
            self._draw.line((0, pos, dim_x, pos), width=2, fill="white")

    def _get_sector_pos(self, sector: tuple):
        """Retrive the absolute start and end position of the sector"""

        id_x, id_y = sector

        sector_dim_x = self._screen_dim_x // self._sectors_x
        sector_dim_y = self._screen_dim_y // self._sectors_y

        start_x = sector_dim_x * id_x
        start_y = sector_dim_y * id_y
        end_x = sector_dim_x * (id_x + 1)
        end_y = sector_dim_y * (id_y + 1)

        return start_x, end_x, start_y, end_y

    def _get_sector_center(self, sector: tuple):
        """Retrive the absolute center of the sector"""

        return self._get_coord_center(*self._get_sector_pos(sector))

    def _get_coord_center(self, start_x, end_x, start_y, end_y):
        """Calculate coordinate center"""

        center_x = start_x + (end_x - start_x) // 2
        center_y = start_y + (end_y - start_y) // 2

        return center_x, center_y

    def _check_sector(self, sector: tuple):
        """Check if sector exist with current configuration"""

        return (
            sector[0] < self._sectors_x
            or sector[1] < self._sectors_y
            or sector[0] >= 0
            or sector[1] >= 0
        )

    async def _write_on_screen(
        self, position: tuple, color: tuple, content: str, padding: tuple, font=None
    ):
        """Primitive to write text on screen

        :param position: absolute position on the screen, `(0, 0)` is the top left corner
        :param color: color as a rgb tuple
        :param content: string to write on screen
        :param padding: relative padding inside the sector
        :param font: raw font paramenter
        """

        if self._overlay is None:
            self._new_overlay()

        if font is None:
            font = self._default_font

        if padding:
            # add padding to the position
            position = tuple(map(operator.add, position, padding))

        self._draw.text(position, content, color, font)

    def _adjust_font(self, size, content: str):
        """Adjust font dimension to remain into the sector dimension

        :param size: size of the section with padding
        :param content: string to evaluate length
        """

        font = self._default_font
        while font.getlength(content) >= size:
            font = ImageFont.truetype(self.FONT_PATH, font.size - 5)

        return font

    async def _show_center_guide(self, sector: tuple = None):
        """Show a center cros, if `sector` is `None` show the center of the screen

        :param sector: sector to write
        """

        if sector is None:
            start_x = start_y = 0
            end_x, end_y = self._screen_dim_x, self._screen_dim_y
            center_x, center_y = end_x // 2, end_y // 2
        else:
            start_x, end_x, start_y, end_y = self._get_sector_pos(sector)
            center_x, center_y = self._get_sector_center(sector)

        self._draw.line((center_x, start_y, center_x, end_y), width=2, fill="white")
        self._draw.line((start_x, center_y, end_x, center_y), width=2, fill="white")

    async def _refresh_screen(self, update_rate):
        """Refresh screen and create new frame and overlay

        :param update_rate: number of frame updated in a second
        """

        # instead of using `overlay.update(img.tobytes())` which uses up a lot of memory
        # we have found more convenient to destroy and recreate the overlay.
        # to avoid annoying behaviours we create the overlay before destroying it
        prev = self._overlay

        if prev:
            self._new_overlay()
            self._new_frame()

            self.remove_overlay(prev)

        # sleep before reiterate
        await sleep(1 / update_rate)

    def with_grid(self):
        """Show the grid with the sectors"""

        self._grid = True

    def with_zoom(self, perc: int):
        """Zoom-in the camera, this is a digialt zoom, so it reduce the FOV and the quality of the image

        :param perc: zoom in percentage 0-99
        """

        if perc < 0 or perc >= 100:
            return

        perc /= 100

        off = perc / 2
        roi = 1 - perc

        # zoom api has a tuple (off_x, off_y, roi_h, roi_w)
        # for maintaing the same screen proportion
        # they must be the same two by two
        self.zoom = (off, off, roi, roi)

    def with_overlay_data(self, data: dict):
        """Referance data for the overlay"""

        OverlayElement.DATA = data

    def add_overlay_element(self, element: OverlayElement):
        """Insert an element in the overlay grid"""

        self._overlay_element_list.append(element)

    async def start_with_overlay(self, update_rate=2):
        """Start preview with the overlay

        The data to track must be specified with the function `with_overlay_data`. Inside of this is called a loop to keep updated screen data

        :param update_rate: number of times the overlay data are updated in a second [default=2]
        """

        self._new_frame()
        self.start_preview()

        while True:
            for elem in self._overlay_element_list:
                if elem.is_multiline():
                    await self.write_on_multi_sector(
                        *elem.to_writable(), len(elem), elem.direction
                    )
                else:
                    await self.write_on_sector(*elem.to_writable())

            await self._refresh_screen(update_rate)

    async def write_on_sector(
        self, sector: tuple, color: tuple, content: str or None, padding=(0, -15)
    ):
        """Write text in a screen sector

        :param sector: tuple to identify the sector, `(0, 0)` is the top left corner sector
        :param color: color as a rgb tuple
        :param content: string to write on screen
        :param padding: relative padding inside the sector [default=(0, -15)]
        """

        if content is None:
            return

        # check if the sector exist
        if not self._check_sector(sector):
            return

        start_x, end_x, _, _ = self._get_sector_pos(sector)
        center_x, center_y = self._get_sector_center(sector)

        font = self._adjust_font(end_x - start_x - padding[0], content)
        content_size_x, content_size_y = font.getsize(content)

        pos = (center_x - content_size_x // 2, center_y - content_size_y // 2)

        await self._write_on_screen(pos, color, content, padding, font)

    async def write_on_multi_sector(
        self,
        start_sector: tuple,
        color: tuple,
        content: str,
        length: int,
        direction_row: bool = True,
        padding=(0, -15),
    ):
        """Write text in multiple screen sectors

        :param start_sector: tuple to indentify the starting sector, `(0, 0)` is the top left corner sector
        :param color: color as a rgb tuple
        :param content: string to write on screen
        :param length: total number of sectors to write
        :param direction_row: `True` to write on the row, `False` to write on the column
        :param padding: relative padding inside the sector [default=(0, -15)]
        """

        if content is None or length <= 1:
            return

        if direction_row:
            end_sector = (start_sector[0] + length - 1, start_sector[1])
        else:
            end_sector = (start_sector[0], start_sector[1] + length - 1)

        # check if the sectors exist
        if not self._check_sector(start_sector) or not self._check_sector(end_sector):
            return

        start_x, _, start_y, _ = self._get_sector_pos(start_sector)
        _, end_x, _, end_y = self._get_sector_pos(end_sector)
        center_x, center_y = self._get_coord_center(start_x, end_x, start_y, end_y)

        font = self._adjust_font(end_x - start_x - padding[0], content)
        content_size_x, content_size_y = font.getsize(content)

        pos = (center_x - content_size_x // 2, center_y - content_size_y // 2)

        await self._write_on_screen(pos, color, content, padding, font)
