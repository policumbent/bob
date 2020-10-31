import json


class Settings:
    def __init__(self, values):
        assert isinstance(values, dict) or isinstance(values, Settings)

        if isinstance(values, dict):
            self._values = values
        elif isinstance(values, Settings):
            self._values = values.values

    @property
    def values(self) -> dict:
        return self._values

    def save(self):
        with open('config.json', 'w') as json_file:
            json.dump(self._values, json_file)

    def load(self):
        try:
            with open('config.json') as json_file:
                self._values = json.load(json_file)
        except Exception as e:
            print(e)
            self._values = {}

    @property
    def accelerometer_samples(self) -> int:
        return self._values['accelerometer_samples'] \
            if self._values.__contains__('accelerometer_samples') \
               and isinstance(self._values['accelerometer_samples'], int) \
            else 1000


class MexPriority:
    very_low = 1
    low = 2
    medium = 3
    high = 4
    very_high = 5


class MexType:
    default = 0
    trap = 1
