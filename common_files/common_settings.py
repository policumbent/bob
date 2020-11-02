import json


class CommonSettings:
    def __init__(self, values):
        assert isinstance(values, dict) or isinstance(values, CommonSettings)

        if isinstance(values, dict):
            self._values = values
        elif isinstance(values, CommonSettings):
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
