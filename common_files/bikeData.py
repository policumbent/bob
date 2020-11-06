import json


class BikeData:
    def __init__(self, sensors: list):
        self.deviceTypeInt: int = 2
        self._sensors = sensors
        # MANAGER DATA
        if sensors.__contains__('manager'):
            self.timeStr: str = ''
            self.bikeName: str = 'taurusx'
            self.cpuTemp: int = 0
            self.time: int = 0

        # ANT DATA
        if sensors.__contains__('ant'):
            self.heartrate: int = 0
            self.speed: float = 0
            self.distance: int = 0
            self.power: int = 0
            self.cadence: int = 0

        # GPS DATA
        if sensors.__contains__('gps'):
            self.timestamp: str = '00-01-01 00:00:00'
            self.time: float = 0.0
            self.speedGps: float = 0.0
            self.latitude: float = 0.0
            self.longitude: float = 0.0

        # GEAR DATA
        if sensors.__contains__('gear'):
            self.gear: int = 0

        # POWER SPEED TARGET DATA
        if sensors.__contains__('power_speed_target'):
            self.targetSpeed: float = 0.0
            self.targetPower: float = 0.0

        # MESSAGES
        if sensors.__contains__('messages'):
            self.line1: str = ''
            self.line2: str = ''

    # TODO: CONTROLLARE CHE PARAMETRI SIANO PRESENTI

    def set_manager(self, values: dict):
        if not self._sensors.__contains__('manager'):
            return
        self.timeStr = values['time_str']
        self.time = values['time_int']
        self.cpuTemp = values['temperature']
        self.bikeName = values['bike']

    def set_ant(self, values: dict):
        if not self._sensors.__contains__('ant'):
            return
        self.heartrate = values['heartrate']
        self.speed = values['speed']
        self.distance = values['distance']
        self.power = values['1s_power']
        self.cadence = values['cadence']

    def set_gps(self, values: dict):
        if not self._sensors.__contains__('gps'):
            return
        self.timestamp = values['timestamp']
        self.latitude = values['latitude']
        self.longitude = values['longitude']
        self.speedGps = values['speedGPS']

    def set_gear(self, values: dict):
        if not self._sensors.__contains__('gear'):
            return
        self.gear = values['gear']

    def set_power_speed_target(self, values: dict):
        if not self._sensors.__contains__('power_speed_target'):
            return
        self.targetPower = values['target_power']
        self.targetSpeed = values['target_speed']

    def set_messages(self, values: dict):
        if not self._sensors.__contains__('messages'):
            return
        self.line1 = values['line_1']
        self.line2 = values['line_2']

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
