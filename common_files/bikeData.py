import json


class BikeData:
    def __init__(self, sensors: list):
        self.deviceTypeInt: int = 2
        self._sensors = sensors
        # MANAGER DATA
        if sensors.__contains__('manager'):
            # self.__timeStr: str = ''
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
            self.__accX: float = 0
            self.__accY: float = 0
            self.__accZ: float = 0
            self.__accXMax: float = 0
            self.__accYMax: float = 0
            self.__accZMax: float = 0

        # GPS DATA
        if sensors.__contains__('gps'):
            self.__timestamp: str = '00-01-01 00:00:00'
            self.__speedGps: float = 0.0
            self.__latitude: float = 0.0
            self.__longitude: float = 0.0
            self.__satellites: int = 0

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

        # HALL SENSOR
        if sensors.__contains__('hall_sensor'):
            self.__speed_2: float = 0.0
            self.__distance_2: float = 0.0

        # WEATHER
        if sensors.__contains__('weather'):
            self.__temperature: float = 0.0
            self.__humidity: float = 0.0

    # TODO: CONTROLLARE CHE PARAMETRI SIANO PRESENTI

    def set_manager(self, values: dict):
        if not self._sensors.__contains__('manager'):
            return
        try:
            # if values.__contains__('time_str'):
            #     self.__timeStr = str(values['time_str'])
            if values.__contains__('time_int'):
                self.__time = int(values['time_int'])
            if values.__contains__('cpu_temperature'):
                self.__cpuTemp = int(values['cpu_temperature'])
            if values.__contains__('bike'):
                self.__bikeName = str(values['bike'])
        except Exception as e:
            print(e)

    def set_ant(self, values: dict):
        # print('set', values)
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

    def set_hall_sensor(self, values: dict):
        if not self._sensors.__contains__('hall_sensor'):
            return
        try:
            if values.__contains__('speed_2'):
                self.__speed_2 = float(values['speed_2'])
            if values.__contains__('distance_2'):
                self.__distance_2 = float(values['distance_2'])
        except Exception as e:
            print(e)

    def set_weather(self, values: dict):
        if not self._sensors.__contains__('weather'):
            return
        try:
            if values.__contains__('temperature'):
                self.__temperature = float(values['temperature'])
            if values.__contains__('humidity'):
                self.__humidity = float(values['humidity'])
        except Exception as e:
            print(e)

    def set_accelerometer(self, values: dict):
        if not self._sensors.__contains__('accelerometer'):
            return
        try:
            if values.__contains__('x_avg'):
                self.__accX = float(values['x_avg'])
            if values.__contains__('y_avg'):
                self.__accY = float(values['y_avg'])
            if values.__contains__('z_avg'):
                self.__accZ = float(values['z_avg'])
            if values.__contains__('x_max'):
                self.__accXMax = float(values['x_max'])
            if values.__contains__('y_max'):
                self.__accYMax = float(values['y_max'])
            if values.__contains__('z_max'):
                self.__accZMax = float(values['z_max'])
        except Exception as e:
            print(e)

    def set_gps(self, values: dict):
        if not self._sensors.__contains__('gps'):
            return
        try:
            if values.__contains__('timestamp'):
                self.__timestamp = str(values['timestamp'])
            if values.__contains__('latitude'):
                self.__latitude = float(values['latitude'])
            if values.__contains__('longitude'):
                self.__longitude = float(values['longitude'])
            if values.__contains__('speedGPS'):
                self.__speedGps = float(values['speedGPS'])
            if values.__contains__('satellites'):
                self.__satellites = int(values['satellites'])
        except Exception as e:
            print(e)

    def set_gear(self, values: dict):
        if not self._sensors.__contains__('gear'):
            return
        try:
            if values.__contains__('gear'):
                self.__gear = int(values['gear'])
        except Exception as e:
            print(e)

    def set_power_speed_target(self, values: dict):
        if not self._sensors.__contains__('power_speed_target'):
            return
        try:
            if values.__contains__('target_power'):
                self.__targetPower = float(values['target_power'])
            if values.__contains__('target_speed'):
                self.__targetSpeed = float(values['target_speed'])
        except Exception as e:
            print(e)

    def set_messages(self, values: dict):
        if not self._sensors.__contains__('messages'):
            return
        try:
            if values.__contains__('line_1'):
                self.__line1 = str(values['line_1'])
            if values.__contains__('line_2'):
                self.__line2 = str(values['line_2'])
        except Exception as e:
            print(e)

    def to_json(self) -> dict:
        elements = self.__dict__.copy()
        elements.pop('_sensors', None)
        v = json.dumps(elements, sort_keys=True, indent=4)
        v = v.replace('_BikeData__', '')
        return json.loads(v)

    def get_keys(self) -> list:
        return list(self.to_json().keys())

    # MANAGER DATA
    @property
    def bike_name(self):
        return self.__bikeName

    # @property
    # def time_str(self):
    #     return self.__timeStr

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

    @property
    def satellites(self):
        return self.__satellites

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
