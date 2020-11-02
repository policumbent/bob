from .common_settings import CommonSettings
from .message import MexPriority


class Settings(CommonSettings):
    @property
    def vel_power_target_csv(self) -> str:
        return self._values['vel_power_target_csv'] \
            if self._values.__contains__('vel_power_target_csv') \
               and isinstance(self._values['vel_power_target_csv'], int) \
            else 'test_Vittoria.csv'
