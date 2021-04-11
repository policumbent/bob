import threading
import time
from mpu6050 import mpu6050

from .sensor import Sensor
from .settings import Settings
from .alert import Alert, AlertPriority
from .message import Message, MexPriority

axis = ['x', 'y', 'z']


class Accelerometer(Sensor):
    def export(self):
        with self._value_lock:
            return self._values.copy()

    def update_settings(self, settings: Settings):
        pass

    def signal(self, value: str):
        if value == 'accel_set_zero':
            self._send_alert(Alert('Calibrazione accelerometro effettuata', AlertPriority.low))
            self._send_message(Message('Calibrazione accelerometro effettuata', MexPriority.low))
            self._zero_count = True
        elif value == 'reset':
            self._max_reset()

    def __init__(self, settings: Settings, send_alert, send_message):
        self._send_alert = send_alert
        self._send_message = send_message
        self._sensor = mpu6050(0x68)
        self._n_samples = settings.accelerometer_samples
        self._zero_count = False
        self._data = dict()
        self._data_avg = dict()
        self._data_max = dict()
        self._data_sum = dict()
        self._data_zero = dict()
        self._values = dict()
        self._value_lock = threading.Lock()
        for a in axis:
            self._data_zero[a] = 0
            self._data[a] = [0]*self._n_samples
            # i massimi (e anche le medie) sono in valore assoluto
            self._data_avg[a] = 0
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    @property
    def sensor(self):
        return self._sensor

    @property
    def n_samples(self):
        return self._n_samples

    @property
    def data(self):
        return self._data

    def _is_abnormal(self, max_values: dict):
        pass

    def _get_data(self, i):
        sensor_data = self._sensor.get_accel_data()
        if self._zero_count:
            for a in axis:
                self._data_zero[a] = sensor_data[a]
            self._zero_count = False
        for a in axis:
            self._data[a][i] = sensor_data[a] - self._data_zero[a]

    def _update_values(self, i):
        for a in axis:
            if abs(self._data[a][i]) > self._data_max[a]:
                self._data_max[a] = abs(self._data[a][i])
            self._data_sum[a] += abs(self._data[a][i])

    def _max_reset(self):
        with self._value_lock:
            for a in axis:
                self._data_max[a] = 0

    # def _print_data(self):
    #     print("x max: " + str(self._data_max["x"]) + ", x avg: " + str(self._data["x_avg"]))
    #     print("y max: " + str(self._data_max["y"]) + ", y avg: " + str(self._data["y_avg"]))
    #     print("z max: " + str(self._data_max["z"]) + ", z avg: " + str(self._data["z_avg"]))
    #     print('\n')

    def _init_values(self):
        # i massimi (e anche le medie) sono in valore assoluto
        for a in axis:
            self._data_max[a] = 0
            self._data_sum[a] = 0

    def _run(self):
        while True:
            self._init_values()  # Inizializza massimi e somme

            for i in range(self._n_samples):
                self._get_data(i)  # Legge i dati dall'accelerometro
                self._update_values(i)  # Aggiorna massimi e somme

            for a in axis:
                self._data_avg[a] = self._data_sum[a] / self._n_samples

            with self._value_lock:
                self._values = {
                    'x_avg':  round(self._data_avg["x"], 2),
                    'y_avg':  round(self._data_avg["y"], 2),
                    'z_avg':  round(self._data_avg["z"], 2),
                    'x_max':  round(self._data_max["x"], 2),
                    'y_max':  round(self._data_max["y"], 2),
                    'z_max':  round(self._data_max["z"], 2)
                }
