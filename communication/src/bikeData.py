import json
from .settings import Settings


class BikeData:
    def __init__(self):
        self.deviceTypeInt: int = 2

        # MANAGER DATA
        self.bikeName: str = 'taurusx'
        self.cpuTemp: int = 0
        self.time: int = 0

        # ANT DATA
        self.heartrate: int = 0
        self.speed: int = 0
        self.distance: int = 0
        self.power: int = 0

        # GPS DATA
        self.timestamp: str = '00-01-01 00:00:00'
        self.speed: float = 0.0
        self.time: float = 0.0
        self.speedGps: float = 0.0
        self.latitude: float = 0.0
        self.longitude: float = 0.0

    def set_manager(self, values: dict):
        self.time = values['time_int']
        self.cpuTemp = values['temperature']
        self.bikeName = values['bike']

    def set_ant(self, values: dict):
        self.heartrate = values['heartrate']
        self.speed = values['speed']
        self.distance = values['distance']
        self.power = values['1s_power']

    def set_gps(self, values: dict):
        self.timestamp = values['timestamp']
        self.latitude = values['latitude']
        self.longitude = values['longitude']
        self.speedGps = values['speedGPS']
        self.speedGps = values['speedGPS']

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
