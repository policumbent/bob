from .common_settings import CommonSettings
from .message import MexPriority


class Settings(CommonSettings):
    @property
    def trap_priority(self) -> int:
        return self._values['trap_priority'] \
            if self._values.__contains__('trap_priority') \
               and isinstance(self._values['trap_priority'], int) \
            else MexPriority.low
