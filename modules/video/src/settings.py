from .common_files.common_settings import CommonSettings
import json


class Settings(CommonSettings):
    def __init__(self, values: dict, name):
        super(Settings, self).__init__(values, name)
        self._video = True
        self._USB_PATH = '/home/pi/'
        self._default_color_1 = [255, 255, 255]
        self._default_color_2 = [0, 0, 0]

    @property
    def power_speed_simulator(self) -> bool:
        return self._values['power_speed_simulator'] \
            if self._values.__contains__('power_speed_simulator') \
            and isinstance(self._values['power_speed_simulator'], bool) \
            else False

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

    @property
    def lap_position(self) -> bool:
        return self._values['lap_position'] \
            if self._values.__contains__('lap_position') \
            and isinstance(self._values['lap_position'], bool) \
            else False

    @property
    def track_length(self) -> int:
        return self._values['track_length'] \
            if self._values.__contains__('track_length') \
            and isinstance(self._values['track_length'], int) \
            else 8000




