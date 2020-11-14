from .common_settings import CommonSettings
from .message import MexPriority
import json


class Settings(CommonSettings):
    @property
    # todo: aggiungere tipo di ritorno
    def gear(self):
        # todo: controllare che sia nel formato corretto
        return self._values['gear'] \
            if self._values.__contains__('gear') \
            else \
            {
                'gear': {
                    'up_positions_s1': [49, 60, 70, 78, 92, 99, 108, 120, 131, 141, 170],
                    'up_positions_s2': [171, 156, 143, 133, 115, 106, 93, 78, 64, 51, 12],
                    'down_positions_s1': [49, 63, 71, 78, 88, 97, 107, 118, 131, 141, 153],
                    'own_positions_s2': [171, 152, 142, 132, 120, 108, 94, 80, 64, 51, 35]
                }
            }

    @gear.setter
    def gear_settings(self, value):
        # todo: controllare che sia nel formato corretto
        self._values['gear'] = value

