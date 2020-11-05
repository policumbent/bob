import csv
import threading

from .sensor import Sensor
from .settings import Settings


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

    def __init__(self, settings: Settings):
        self._settings = settings
        self._file_lock = threading.Lock()

        self._exist = False
        self._file = None
        self._state = False
        self._csv = None
        self._line = (0, 0, 0)
        self._line_count = 0
        self.open_file()

    def open_file(self):
        with self._file_lock:
            try:
                self._file = open("power_speed_profiles/" + self._settings.vel_power_target_csv, "r")
                self._exist = True
                self._state = True
                self._csv = csv.reader(self._file, delimiter=',')
                self._line_count = 0
                self._line = next(self._csv, None)
            except FileNotFoundError:
                print("File simulator non esistente")
                self._exist = False
                self._line = (0, 0, 0)

    @property
    def state(self):
        return self._state

    def reset(self):
        self._exist = False
        self._file.close()
        self.open_file()

    def refresh(self, distance):
        with self._file_lock:
            # todo: togliere il try catch
            if not self._exist:
                return
            try:
                if self._line is None:
                    return
                self._line_count += 1
                while int(self._line[0]) < distance:
                    self._line = next(self._csv, None)
                    if self._line is None:
                        self._state = False
                        return
                    # print("Distance: ", self._line[0])
                    # print("Speed: ", round(float(self._line[1]) * 3.6, 2))
                    # print("Power: ", self._line[2])
            except Exception as e:
                print(e)
                print("Errore power speed simulator")

    def get(self):
        return self._line

    @property
    def target_speed(self):
        return round(float(self._line[1]) * 3.6, 2)

    @property
    def target_power(self):
        return round(float(self._line[2]))

    def get_running(self):
        return self._state


# p = PowerEstimator()
# p.refresh(10)
