import json


class WeatherData:
    def __init__(self, weather: dict):
        self._stationId: int = weather['stationId']
        self._timestamp: str = weather['timestamp']
        self._windSpeed: float = weather['windSpeed']
        self._temperature: float = weather['temperature']
        self._humidity: float = weather['humidity']
        self._pressure: float = weather['pressure']
        self._windDirection: float = weather['windDirection']
        self._latitude: float = weather['latitude']
        self._longitude: float = weather['longitude']

    def to_json(self):
        elements = self.__dict__.copy()
        v = json.dumps(elements, sort_keys=True, indent=4)
        v = v.replace('_', '')
        return json.loads(v)

    @property
    def station_id(self):
        return self._stationId
