from .common_settings import CommonSettings
from .message import MexPriority
import json


class Settings(CommonSettings):
    def __int__(self):
        self.video = True
        self.USB_PATH = '/home/pi/'
        self.default_color_1 = [255, 255, 255]
        self.default_color_2 = [0, 0, 0]

    @property
    def video(self) -> bool:
        return self.video

    @property
    def USB_PATH(self) -> str:
        return self.USB_PATH

    @property
    def default_color_1(self) -> list:
        return self.default_color_1

    @property
    def default_color_2(self) -> list:
        return self.default_color_2

    @property
    def video_record(self) -> bool:
        return self._values['video_record'] \
            if self._values.__contains__('video_record') \
               and isinstance(self._values['video_record'], bool) \
            else False

    # @property
    # def bike(self) -> str:
    #     return self._values['bike'] \
    #         if self._values.__contains__('bike') \
    #            and isinstance(self._values['bike'], str) \
    #         else 'taurusx'


