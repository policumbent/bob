import threading
from .steGPS import Gps
# Define RX and TX pins for the board's serial port connected to the GPS.
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
# RX = board.D18
# TX = board.D19
from .settings import Settings


class GpsInterface():

    def __init__(
        self,
        latitude_start: float,
        longitude_start: float,
        latitude_end: float,
        longitude_end: float,
        serial_port: str,
    ):
        self._latitude_start = latitude_start
        self._longitude_start = longitude_start
        self._latitude_end = latitude_end
        self._longitude_end = longitude_end
        self._gps = Gps(serial_port)

    def read_data(self):
        return {
            'timestampGPS': self._gps.timestamp,
            'latitude': round(self._gps.latitude, 6),
            'longitude': round(self._gps.longitude, 6),
            'altitude': self._gps.altitude,
            'speedGPS': round(self._gps.speed, 2),
            'distanceGPS': self._gps.travelled_distance,
            'satellites': self._gps.satellites,
            'distance2timing': self.distance2timing()
        }
    
    # it returns distance from rider position to timing zone
    def distance2timing(self):
        # if distance to the end of time zone is less than distance to start of it
        # it means that timing zone is already passed by the rider
        distance_to_start = self._gps.distance(self._latitude_start, self._longitude_end)
        distance_to_end = self._gps.distance(self._latitude_end, self._longitude_end)
        if distance_to_start > distance_to_end:
            return 0.0
        return distance_to_start 

    def reset_distance(self):
        self._gps.travelled_distance = 0
