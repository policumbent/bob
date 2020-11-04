from .common_settings import CommonSettings
from .message import MexPriority
import json


class Settings(CommonSettings):
    @property
    def max_temp(self) -> int:
        return self._values['max_temp'] \
            if self._values.__contains__('max_temp') \
               and isinstance(self._values['max_temp'], int) \
            else 70

    @property
    def autopause(self) -> int:
        return self._values['autopause'] \
            if self._values.__contains__('autopause') \
               and isinstance(self._values['autopause'], int) \
            else False

    @property
    def bike(self) -> str:
        return self._values['bike'] \
            if self._values.__contains__('bike') \
               and isinstance(self._values['bike'], str) \
            else 'taurusx'

