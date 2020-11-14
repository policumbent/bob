from .common_settings import CommonSettings
from .message import MexPriority
import json


class Settings(CommonSettings):
    def __init__(self, values: dict):
        super(Settings, self).__init__(values)
        self._video = True
        self._power_speed_simulator = True
        self._USB_PATH = '/home/pi/'
        self._default_color_1 = [255, 255, 255]
        self._default_color_2 = [0, 0, 0]

    @property
    def power_speed_simulator(self) -> bool:
        return self._power_speed_simulator

    @property
    def video(self) -> bool:
        return self._video

    @property
    def usb_path(self) -> str:
        return self._USB_PATH

    @property
    def default_color_1(self):
        return self._default_color_1

    @property
    def default_color_2(self) -> list:
        return self._default_color_2

    @property
    def video_record(self) -> bool:
        return self._values['video_record'] \
            if self._values.__contains__('video_record') \
            and isinstance(self._values['video_record'], bool) \
            else False




