from .common_files.common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def accelerometer_samples(self) -> int:
        return self._values['accelerometer_samples'] \
            if self._values.__contains__('accelerometer_samples') \
               and isinstance(self._values['accelerometer_samples'], int) \
            else 1000
