import json


class BikeData:
    def __init__(self, sensors: list):
        self.deviceTypeInt: int = 2
        self._sensors = sensors
        # MANAGER DATA
        if sensors.__contains__('manager'):
            self.__timeStr: str = ''
            self.__bikeName: str = 'taurusx'
            self.__cpuTemp: int = 0
            self.__time: int = 0

        # ANT DATA
        if sensors.__contains__('ant'):
            self.__heartrate: int = 0
            self.__speed: float = 0
            self.__distance: int = 0
            self.__power: int = 0
            self.__cadence: int = 0

        # GPS DATA
        if sensors.__contains__('gps'):
            self.__timestamp: str = '00-01-01 00:00:00'
            self.__speedGps: float = 0.0
            self.__latitude: float = 0.0
            self.__longitude: float = 0.0

        # GEAR DATA
        if sensors.__contains__('gear'):
            self.__gear: int = 0

        # POWER SPEED TARGET DATA
        if sensors.__contains__('power_speed_target'):
            self.__targetSpeed: float = 0.0
            self.__targetPower: float = 0.0

        # MESSAGES
        if sensors.__contains__('messages'):
            self.__line1: str = ''
            self.__line2: str = ''

    # TODO: CONTROLLARE CHE PARAMETRI SIANO PRESENTI

    def set_manager(self, values: dict):
        if not self._sensors.__contains__('manager'):
            return
        self.__timeStr = values['time_str']
        self.__time = values['time_int']
        self.__cpuTemp = values['temperature']
        self.__bikeName = values['bike']

    def set_ant(self, values: dict):
        if not self._sensors.__contains__('ant'):
            return
        self.__heartrate = values['heartrate']
        self.__speed = values['speed']
        self.__distance = values['distance']
        self.__power = values['1s_power']
        self.__cadence = values['cadence']

    def set_gps(self, values: dict):
        if not self._sensors.__contains__('gps'):
            return
        self.__timestamp = values['timestamp']
        self.__latitude = values['latitude']
        self.__longitude = values['longitude']
        self.__speedGps = values['speedGPS']

    def set_gear(self, values: dict):
        if not self._sensors.__contains__('gear'):
            return
        self.__gear = values['gear']

    def set_power_speed_target(self, values: dict):
        if not self._sensors.__contains__('power_speed_target'):
            return
        self.__targetPower = values['target_power']
        self.__targetSpeed = values['target_speed']

    def set_messages(self, values: dict):
        if not self._sensors.__contains__('messages'):
            return
        self.__line1 = values['line_1']
        self.__line2 = values['line_2']

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    # MANAGER DATA
    @property
    def bike_name(self):
        if isinstance(self.__bikeName, str):
            return self.__bikeName

    @property
    def cpu_temp(self):
        if isinstance(self.__cpuTemp, int):
            return self.__cpuTemp

    @property
    def time(self):
        if isinstance(self.__time, int):
            return self.__time

    # ANT DATA

    @property
    def heartrate(self):
        if isinstance(self.__heartrate, int):
            return self.__heartrate

    @property
    def speed(self):
        if isinstance(self.__speed, float):
            return self.__speed \


    @property
    def distance(self):
        if isinstance(self.__distance, int):
            return self.__distance \


    @property
    def power(self):
        if isinstance(self.__power, int):
            return self.__power \


    @property
    def cadence(self):
        if isinstance(self.__cadence, int):
            return self.__cadence

    # GPS DATA

    @property
    def time_stamp(self):
        if isinstance(self.__timestamp, str):
            return self.__timestamp\


    @property
    def speed_gps(self):
        if isinstance(self.__speedGps, float):
            return self.__speedGps\


    @property
    def latitude(self):
        if isinstance(self.__latitude, float):
            return self.__latitude\


    @property
    def longitude(self):
        if isinstance(self.__longitude, float):
            return self.__longitude\


    # GEAR DATA

    @property
    def gear(self):
        if isinstance(self.__gear, int):
            return self.__gear

    # POWER SPEED TARGET DATA

    @property
    def target_speed(self):
        if isinstance(self.__targetSpeed, float):
            return self.__targetSpeed\


    @property
    def target_power(self):
        if isinstance(self.__targetPower, float):
            return self.__targetPower

    # MESSAGES DATA

    @property
    def line1(self):
        if isinstance(self.__line1, str):
            return self.__line1\


    @property
    def line2(self):
        if isinstance(self.__line2, float):
            return self.__line2
