from .common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def latitude_timing_start(self) -> float:
        return self._values['latitude_timing_start'] \
            if self._values.__contains__('latitude_timing_start') \
               and isinstance(self._values['latitude_timing_start'], float) \
            else 45.032888

    @property
    def longitude_timing_start(self) -> float:
        return self._values['longitude_timing_start'] \
            if self._values.__contains__('longitude_timing_start') \
               and isinstance(self._values['longitude_timing_start'], float) \
            else 7.792347

    @property
    def latitude_timing_end(self) -> float:
        return self._values['latitude_timing_end'] \
            if self._values.__contains__('latitude_timing_end') \
               and isinstance(self._values['latitude_timing_end'], float) \
            else 45.032888

    @property
    def longitude_timing_end(self) -> float:
        return self._values['longitude_timing_end'] \
            if self._values.__contains__('longitude_timing_end') \
               and isinstance(self._values['longitude_timing_end'], float) \
            else 7.792347
