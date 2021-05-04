from .common_files.common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def pin(self) -> int:
        return self._values['pin'] \
            if self._values.__contains__('pin') \
               and isinstance(self._values['pin'], int) \
            else 24

    @property
    def circumference(self) -> int:
        return self._values['circumference'] \
            if self._values.__contains__('circumference') \
               and isinstance(self._values['circumference'], int) \
            else 1450
