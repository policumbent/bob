import time as tm


# TODO: cambiare logica per non far modificare i settings
# TODO: sostituire il dizionario settings con lo state
# TODO: non funziona
from common_files.sensor import Sensor
from .settings import Settings


class Timer(Sensor):
    def __init__(self):
        self.time_i = tm.time()
        self.time_f = 0
        self.count = 0
        self._state_flag = 1

    def signal(self, value: str):
        if value == 'reset':
            self.reset()
        elif value == 'stop':
            self.stop()

    def export(self):
        return {
            'timer': self.str_min
        }

    def update_settings(self, settings: Settings):
        pass

    def __str__(self):
        time = str(round(self.time, 2))
        return '{}s'.format(time)

    @property
    def time(self):
        fin_time = tm.time() if self._state_flag == 1 else self.time_f
        return self.calc_time(fin_time)

    @property
    def time_min(self):
        return round(self.time / 60, 2)

    @property
    def str_min(self):
        minutes = int(self.time_min)
        seconds = round(self.time % 60)
        return f"{minutes}'{seconds}\""

    def set(self, timer):
        self.reset()
        self.count = timer

    def calc_time(self, fin_time):
        return (fin_time - self.time_i) + self.count

    def start(self):
        if self._state_flag != 1:
            self.count = self.time
            self.time_i = tm.time()
            self._state_flag = 1

    def stop(self):
        if self._state_flag != 0:
            self.time_f = tm.time()
            self._state_flag = 0

    def autopause(self):
        if self._state_flag == 1:
            self.stop()
            self._state_flag = 2

    def autostart(self):
        if self._state_flag == 2:
            self.count = self.time
            self.time_i = tm.time()
            self._state_flag = 1

    def reset(self):
        self.stop()
        self.count = 0
        self.time_i = tm.time()
        self._state_flag = 1
        print(str(self))

    def get(self):
        return self.time
