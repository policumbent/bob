import threading
from .steGPS import Gps
from .common_files.sensor import Sensor
# Define RX and TX pins for the board's serial port connected to the GPS.
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
# RX = board.D18
# TX = board.D19
from .settings import Settings


class GpsInterface(Sensor):

    def __init__(self, settings: Settings, timezone_hours=+1):
        self._settings = settings
        self._settings_lock = threading.Lock()
        self._gps = Gps('/dev/ttyAMA1', timezone_hours)

    def signal(self, value: str):
        if value == 'reset':
            self.reset_distance()

    def export(self):
        return {
            'timestamp': self.timestamp,
            'latitude': round(self.latitude, 6),
            'longitude': round(self.longitude, 6),
            'altitude': self.altitude,
            'speedGPS': round(self.speed, 2),
            'distanceGPS': self.travelled_distance,
            'satellites': self.satellites
        }

    def update_settings(self, settings: Settings):
        with self._settings_lock:
            self._settings = settings

    @property
    def position(self):
        return self._gps.position

    @property
    def latitude(self):
        return self._gps.latitude

    @property
    def longitude(self):
        return self._gps.longitude

    @property
    def altitude(self):
        return self._gps.altitude

    @property
    def speed(self):
        return self._gps.speed

    @property
    def satellites(self):
        return self._gps.satellites

    @property
    def day_time(self):
        return self._gps.message_time

    @property
    def date(self):
        return self._gps.date

    @property
    def timestamp(self):
        return self._gps.timestamp

    def distance(self, latitude: float, longitude: float):
        return self._gps.distance(latitude, longitude)

    @property
    def travelled_distance(self):
        return self._gps.travelled_distance

    @property
    def distance2timing(self):
        latitude = float(self._settings.latitude_timing_start)
        longitude = float(self._settings.longitude_timing_start)
        return self._gps.distance(latitude, longitude)

    def reset_distance(self):
        self._gps.travelled_distance = 0

    def is_in_timing(self):
        latitude_start = float(self._settings.latitude_timing_start)
        longitude_start = float(self._settings.longitude_timing_start)
        latitude_end = float(self._settings.latitude_timing_end)
        longitude_end = float(self._settings.longitude_timing_end)
        distance_start = self._gps.distance(latitude_start, longitude_start)
        distance_end = self._gps.distance(latitude_end, longitude_end)
        return distance_end - distance_start < self._settings.trap_length
