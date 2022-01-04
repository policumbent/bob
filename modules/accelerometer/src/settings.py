from core.common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def accelerometer_samples(self) -> int:
        return self._values['accelerometer_samples'] \
            if self._values.__contains__('accelerometer_samples') \
               and isinstance(self._values['accelerometer_samples'], int) \
            else 1000    \

    @property
    def accelerometer_local_csv(self) -> bool:
        return self._values['accelerometer_local_csv'] \
            if self._values.__contains__('accelerometer_local_csv') \
               and isinstance(self._values['accelerometer_local_csv'], bool) \
            else False
