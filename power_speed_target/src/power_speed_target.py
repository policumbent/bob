import csv
import threading

from .sensor import Sensor
from .settings import Settings
from .bikeData import BikeData


# todo: rifare logica
class PowerSpeedTarget(Sensor):
    # todo:
    #  una volta che il file è aperto non posso cambiarlo
    #  o implemento un metodo che lo chiuda e lo riapra se è stato modificato
    #  oppure ignoro questo metodo
    def signal(self, value: str):
        pass

    def export(self):
        return {
            'target_speed': self.target_speed,
            'target_power': self.target_power
        }

    def __init__(self, settings: Settings, bikedata: BikeData):
        self._settings = settings
        self._bikeData = bikedata
        self._file_lock = threading.Lock()
        self._lines = []
        self._exist = False
        self._file = None
        self._state = False
        self._csv = None
        self._line = (0, 0, 0)
        self._line_count = 0
        self._speed = 0.0
        self._power = 0.0
        self.open_file()
        self.refresh()

    def open_file(self):
        with self._file_lock:
            try:
                self._file = open("power_speed_profiles/" + self._settings.vel_power_target_csv, "r")
                self._exist = True
                self._state = True
            except FileNotFoundError:
                print("File simulator non esistente")
                self._exist = False
                self._lines = self._file.readlines()

    @property
    def state(self):
        return self._state

    def reset(self):
        self._exist = False
        self._file.close()
        self.open_file()

    def refresh(self):
        with self._file_lock:
            # todo: togliere il try catch
            if not self._exist:
                return
            while True:
                if len(self._lines < self._bikeData.distance):
                    return
                line = self._lines[self._bikeData.distance]
                dis, self._speed, self._power = line.split(',')
                self._bikeData.set_power_speed_target(self.export())

    def get(self):
        return self._line

    @property
    def target_speed(self):
        return round(float(self._speed * 3.6, 2))

    @property
    def target_power(self):
        return round(float(self._power))

    def get_running(self):
        return self._state


# p = PowerEstimator()
# p.refresh(10)
