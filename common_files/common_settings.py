import json
from os import makedirs


class CommonSettings:
    def __init__(self, values, module_name: str):
        assert isinstance(values, dict) or isinstance(values, CommonSettings)

        if isinstance(values, dict):
            self._values = values
        elif isinstance(values, CommonSettings):
            self._values = values.values
        self.__name = module_name

    @property
    def values(self) -> dict:
        return self._values

    def save(self):
        try:
            makedirs(f'../../BOB_CONFIG/{self.__name}', exist_ok=True)
            with open(f'../../BOB_CONFIG/{self.__name}/config.json', 'w') as json_file:
                json.dump(self._values, json_file)
        except Exception as e:
            print(e)

    def load(self):
        try:
            makedirs(f'../../BOB_CONFIG/{self.__name}', exist_ok=True)
            with open(f'../../BOB_CONFIG/{self.__name}/config.json') as json_file:
                self._values = json.load(json_file)
        except Exception as e:
            print(e)

    def new_settings(self, settings: dict):
        updated = False
        for s in self._values:
            if settings.__contains__(s):
                self._values[s] = settings[s]
                updated = True
        if updated:
            self.save()
        return updated
