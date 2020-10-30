from typing import List, Dict


class Settings:
    def __init__(self, values):
        assert isinstance(values, dict) or isinstance(values, Settings)

        if isinstance(values, dict):
            self._values = values
        elif isinstance(values, Settings):
            self._values = values.values

        # si potrebbero aggiungere le property dinamicamente con un metodo del genere
        # e accettare solo i dict corretti
        # for e in required_params:
        #     self.e = property(lambda x: self._values[e])

    @property
    def values(self) -> dict:
        return self._values

    def save(self):
        # todo: salva i settings su file
        pass

    @property
    def bike(self) -> str:
        return self._values['bike'] if self._values.__contains__('bike') \
           and isinstance(self._values['bike'], str) else '0'

    @property
    def marta_xbee_address(self) -> str:
        value = self._values['marta_xbee_address']
        return value if value is not None and isinstance(value, str) else '0'

    @property
    def vel_power_target_csv(self) -> str:
        value = self._values['vel_power_target_csv']
        return value if value is not None and isinstance(value, str) else 'test_Vittoria.csv'

    @property
    def autopause(self) -> bool:
        return self._values['autopause'] \
            if self._values.__contains__('autopause') \
               and isinstance(self._values['autopause'], bool) \
            else False

    @property
    def communication(self) -> bool:
        return self._values['communication'] \
            if self._values.__contains__('communication') \
               and isinstance(self._values['communication'], bool) \
            else False

    @property
    def ant(self) -> bool:
        return self._values['ant'] \
            if self._values.__contains__('ant') \
               and isinstance(self._values['ant'], bool) \
            else False

    @property
    def run_length(self) -> int:
        return self._values['run_length'] \
            if self._values.__contains__('run_length') \
               and isinstance(self._values['run_length'], int) \
            else 8046

    @property
    def accelerometer_samples(self) -> int:
        return self._values['accelerometer_samples'] \
            if self._values.__contains__('accelerometer_samples') \
               and isinstance(self._values['accelerometer_samples'], int) \
            else 1000

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
    def max_temp(self) -> int:
        return self._values['max_temp'] \
            if self._values.__contains__('max_temp') \
               and isinstance(self._values['max_temp'], int) \
            else 80

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

    @property
    def latitude_timing_start(self) -> float:
        return self._values['latitude_timing_start'] \
            if self._values.__contains__('latitude_timing_start') \
               and isinstance(self._values['latitude_timing_start'], float) \
            else '45.032888'

    @property
    def longitude_timing_start(self) -> float:
        return self._values['longitude_timing_start'] \
            if self._values.__contains__('longitude_timing_start') \
               and isinstance(self._values['longitude_timing_start'], float) \
            else '7.792347'

    @property
    def latitude_timing_end(self) -> float:
        return self._values['latitude_timing_end'] \
            if self._values.__contains__('latitude_timing_end') \
               and isinstance(self._values['latitude_timing_end'], float) \
            else '45.032888'

    @property
    def longitude_timing_end(self) -> float:
        return self._values['longitude_timing_end'] \
            if self._values.__contains__('longitude_timing_end') \
               and isinstance(self._values['longitude_timing_end'], float) \
            else '7.792347'

    @property
    # todo: aggiungere tipo di ritorno
    def gear_settings(self):
        # todo: controllare che sia nel formato corretto
        return self._values['gear_settings'] \
            if self._values.__contains__('gear_settings') \
            else \
            {
                'up_positions_s1': [49, 60, 70, 78, 92, 99, 108, 120, 131, 141, 170],
                'up_positions_s2': [171, 156, 143, 133, 115, 106, 93, 78, 64, 51, 12],
                'down_positions_s1': [49, 63, 71, 78, 88, 97, 107, 118, 131, 141, 153],
                'down_positions_s2': [171, 152, 142, 132, 120, 108, 94, 80, 64, 51, 35]
            }

    @gear_settings.setter
    def gear_settings(self, value):
        # todo: controllare che sia nel formato corretto
        self._values['gear_settings'] = value

    # todo: da finire con le property

    def load(self):
        pass
