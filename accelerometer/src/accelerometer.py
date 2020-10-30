import threading
import time
from mpu6050 import mpu6050

from .sensor import Sensor
from .settings import Settings


class Accelerometer(Sensor):
    def export(self):
        with self._value_lock:
            return self._values.copy()

    def update_settings(self, settings: Settings):
        pass

    def signal(self, value: str):
        if value == 'accel_set_zero':
            self._zero_count = True

    def __init__(self, settings: Settings):
        self._sensor = mpu6050(0x68)
        self._n_samples = settings.accelerometer_samples
        self._zero_count = False
        self._data = dict()
        self._values = dict()
        self._value_lock = threading.Lock()
        self._data_zero = {
            'x': 0,
            'y': 0,
            'z': 0
        }
        self._data["x"] = [0]*self._n_samples
        self._data["y"] = [0]*self._n_samples
        self._data["z"] = [0]*self._n_samples
        self._data_max = dict()
        self._data["xAvg"] = 0
        self._data["yAvg"] = 0
        self._data["zAvg"] = 0
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

    def _getData(self, i):
        sensor_data = self._sensor.get_accel_data()
        if self._zero_count:
            self._data_zero['x'] = sensor_data["x"]
            self._data_zero['y'] = sensor_data["y"]
            self._data_zero['z'] = sensor_data["z"]
            self._zero_count = False

        self._data["x"][i] = sensor_data["x"] - self._data_zero['x']
        self._data["y"][i] = sensor_data["y"] - self._data_zero['y']
        self._data["z"][i] = sensor_data["z"] - self._data_zero['z']

    def _updateValues(self, i):
        if abs(self._data["x"][i]) > self._data_max["x"]:
            self._data_max["x"] = abs(self._data["x"][i])
        if abs(self._data["y"][i]) > self._data_max["y"]:
            self._data_max["y"] = abs(self._data["y"][i])
        if abs(self._data["z"][i]) > self._data_max["z"]:
            self._data_max["z"] = abs(self._data["z"][i])

        self.x_sum += abs(self._data["x"][i])
        self.y_sum += abs(self._data["y"][i])
        self.z_sum += abs(self._data["z"][i])

    def _printData(self):
        print("x max: " + str(self._data_max["x"]) + ", x avg: " + str(self._data["xAvg"]))
        print("y max: " + str(self._data_max["y"]) + ", y avg: " + str(self._data["yAvg"]))
        print("z max: " + str(self._data_max["z"]) + ", z avg: " + str(self._data["zAvg"]))
        print('\n')

    def _initValues(self):
        self._data_max["x"] = 0  # i massimi (e anche le medie) sono in valore assoluto
        self._data_max["y"] = 0
        self._data_max["z"] = 0

        self.x_sum = 0
        self.y_sum = 0
        self.z_sum = 0

    def _run(self):
        while True:
            ti = time.time()

            self._initValues()  # Inizializza massimi e somme

            for i in range(self._n_samples):
                self._getData(i) #Legge i dati dall'accelerometro
                self._updateValues(i) #Aggiorna massimi e somme

            self._data["xAvg"] = self.x_sum / self._n_samples
            self._data["yAvg"] = self.y_sum / self._n_samples
            self._data["zAvg"] = self.z_sum / self._n_samples

            with self._value_lock:
                self._values = {
                    'xAvg':  self._data["xAvg"],
                    'yAvg':  self._data["yAvg"],
                    'zAvg':  self._data["zAvg"],
                    'xMax':  self._data_max["x"],
                    'yMax':  self._data_max["y"],
                    'zMax':  self._data_max["z"]
                }
            # tf = time.time()
            # print(tf-ti)
            # self._printData()
