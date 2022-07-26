# NOTE: THIS MUST BE DELETED

from typing import List, Dict
from core.common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def autopause(self) -> bool:
        return self._values['autopause'] \
            if self._values.__contains__('autopause') \
               and isinstance(self._values['autopause'], bool) \
            else False

    @property
    def ant(self) -> bool:
        return self._values['ant'] \
            if self._values.__contains__('ant') \
               and isinstance(self._values['ant'], bool) \
            else False

    @property
    def hour_record(self) -> bool:
        return self._values['hour_record'] \
            if self._values.__contains__('hour_record') \
               and isinstance(self._values['hour_record'], bool) \
            else False

    @property
    def run_length(self) -> int:
        return self._values['run_length'] \
            if self._values.__contains__('run_length') \
               and isinstance(self._values['run_length'], int) \
            else 8046

    @property
    def trap_length(self) -> int:
        return self._values['trap_length'] \
            if self._values.__contains__('trap_length') \
               and isinstance(self._values['trap_length'], int) \
            else 200

    @property
    def hr_sensor_id(self) -> int:
        return self._values['hr_sensor_id'] \
            if self._values.__contains__('hr_sensor_id') \
               and isinstance(self._values['hr_sensor_id'], int) \
            else 0

    @property
    def speed_sensor_id(self) -> int:
        return self._values['speed_sensor_id'] \
            if self._values.__contains__('speed_sensor_id') \
               and isinstance(self._values['speed_sensor_id'], int) \
            else 0

    @property
    def power_sensor_id(self) -> int:
        return self._values['power_sensor_id'] \
            if self._values.__contains__('power_sensor_id') \
               and isinstance(self._values['power_sensor_id'], int) \
            else 0

    @property
    def circumference(self) -> int:
        return self._values['circumference'] \
            if self._values.__contains__('circumference') \
               and isinstance(self._values['circumference'], int) \
            else 1450

    @property
    def average_power_time(self) -> int:
        return self._values['average_power_time'] \
            if self._values.__contains__('average_power_time') \
               and isinstance(self._values['average_power_time'], int) \
            else 3
