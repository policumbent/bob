import json


class BikeData:
    def __init__(self, sensors: list):
        self.deviceTypeInt: int = 2
        self._sensors = sensors
        # MANAGER DATA
        if sensors.__contains__('manager'):
            self.__timeStr: str = ''
            self.__bikeName: str = 'no_bike'
            self.__cpuTemp: int = 0
            self.__time: int = 0

        # ANT DATA
        if sensors.__contains__('ant'):
            self.__heartrate: int = 0
            self.__speed: float = 0
            self.__distance: int = 0
            self.__power: int = 0
            self.__cadence: int = 0

        # ACCELEROMETER DATA
        if sensors.__contains__('accelerometer'):
            self.__xAvg: float = 0
            self.__yAvg: float = 0
            self.__zAvg: float = 0
            self.__xMax: float = 0
            self.__yMax: float = 0
            self.__zMax: float = 0

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
        if values.__contains__('time_str') and isinstance(values['time_str'], str):
            self.__timeStr = values['time_str']
        if values.__contains__('time_int') and isinstance(values['time_int'], int):
            self.__time = values['time_int']
        if values.__contains__('temperature') and isinstance(values['temperature'], int):
            self.__cpuTemp = values['temperature']
        if values.__contains__('bike') and isinstance(values['bike'], str):
            self.__bikeName = values['bike']

    def set_ant(self, values: dict):
        print('set', values)
        if not self._sensors.__contains__('ant'):
            return
        try:
            if values.__contains__('heartrate'):
                self.__heartrate = int(values['heartrate'])
            if values.__contains__('speed'):
                self.__speed = float(values['speed'])
            if values.__contains__('distance'):
                self.__distance = int(values['distance'])
            if values.__contains__('1s_power'):
                self.__power = int(values['1s_power'])
            if values.__contains__('cadence'):
                self.__cadence = int(values['cadence'])
        except Exception as e:
            print(e)

    def set_accelerometer(self, values: dict):
        if not self._sensors.__contains__('accelerometer'):
            return
        if values.__contains__('x_avg') and isinstance(values['x_avg'], float):
            self.__xAvg = values['x_avg']
        if values.__contains__('y_avg') and isinstance(values['y_avg'], float):
            self.__yAvg = values['y_avg']
        if values.__contains__('z_avg') and isinstance(values['z_avg'], float):
            self.__zAvg = values['z_avg']
        if values.__contains__('x_max') and isinstance(values['x_max'], float):
            self.__xMax = values['x_max']
        if values.__contains__('y_max') and isinstance(values['y_max'], float):
            self.__yMax = values['y_max']
        if values.__contains__('z_max') and isinstance(values['z_max'], float):
            self.__zMax = values['z_max']

    def set_gps(self, values: dict):
        if not self._sensors.__contains__('gps'):
            return
        if values.__contains__('timestamp') and isinstance(values['timestamp'], str):
            self.__timestamp = values['timestamp']
        if values.__contains__('latitude') and isinstance(values['latitude'], float):
            self.__latitude = values['latitude']
        if values.__contains__('longitude') and isinstance(values['longitude'], float):
            self.__longitude = values['longitude']
        if values.__contains__('speedGPS') and isinstance(values['speedGPS'], float):
            self.__speedGps = values['speedGPS']

    def set_gear(self, values: dict):
        if not self._sensors.__contains__('gear'):
            return
        if values.__contains__('gear') and isinstance(values['gear'], int):
            self.__gear = values['gear']

    def set_power_speed_target(self, values: dict):
        if not self._sensors.__contains__('power_speed_target'):
            return
        if values.__contains__('target_power') and isinstance(values['target_power'], float):
            self.__targetPower = values['target_power']
        if values.__contains__('target_speed') and isinstance(values['target_speed'], float):
            self.__targetSpeed = values['target_speed']

    def set_messages(self, values: dict):
        if not self._sensors.__contains__('messages'):
            return
        if values.__contains__('line_1') and isinstance(values['line_1'], str):
            self.__line1 = values['line_1']
        if values.__contains__('line_2') and isinstance(values['line_2'], str):
            self.__line2 = values['line_2']

    def to_json(self):
        elements = self.__dict__.copy()
        elements.pop('_sensors', None)
        v = json.dumps(elements, sort_keys=True, indent=4)
        v = v.replace('_BikeData__', '')
        return json.loads(v)

    # MANAGER DATA
    @property
    def bike_name(self):
        return self.__bikeName

    @property
    def time_str(self):
        return self.__timeStr

    @property
    def cpu_temp(self):
        return self.__cpuTemp

    @property
    def time(self):
        return self.__time

    # ANT DATA

    @property
    def heartrate(self):
        return self.__heartrate

    @property
    def speed(self):
        return self.__speed

    @property
    def distance(self):
        return self.__distance

    @property
    def power(self):
        return self.__power

    @property
    def cadence(self):
        return self.__cadence

    # GPS DATA

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def speed_gps(self):
        return self.__speedGps

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    # GEAR DATA

    @property
    def gear(self):
        return self.__gear

    # POWER SPEED TARGET DATA

    @property
    def target_speed(self):
        return self.__targetSpeed

    @property
    def target_power(self):
        return self.__targetPower

    # MESSAGES DATA

    @property
    def line1(self):
        return self.__line1

    @property
    def line2(self):
        return self.__line2
