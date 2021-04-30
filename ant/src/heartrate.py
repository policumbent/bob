from .ant.easy.channel import Channel
import time

from .common_files.sensor import Sensor
from .settings import Settings


class HeartRate(Sensor):
    def __init__(self, settings: Settings):
        self._value = -1
        self._state = False
        self._settings = settings
        self._lastRxTime = time.time()
        self._count = 0

    def signal(self, value: str):
        pass

    def export(self):
        return {
            'heartrate': self.value
        }

    def update_settings(self, settings: Settings):
        pass

    @property
    def state(self):
        return self._state

    @property
    def value(self):
        if (time.time() - self._lastRxTime) > 5:
            self._value = str(0)
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def set_channel(self, channel_hr: Channel):
        # CANALE FREQUENZA CARDIACA
        channel_hr.on_broadcast_data = self.on_data_heartrate
        channel_hr.on_burst_data = self.on_data_heartrate
        channel_hr.set_period(8070)
        channel_hr.set_search_timeout(255)
        channel_hr.set_rf_freq(57)
        # 69  -> ID DELLA MIA FASCIA CARDIO, METTERE 0 PER TUTTE LE FASCIE
        # 120 -> DEVICE ID DEL SENSORE DELLA FC
        hr_sensor_id = self._settings.hr_sensor_id
        channel_hr.set_id(hr_sensor_id, 120, 0)

    def on_data_heartrate(self, data):
        self._state = True
        self.value = str(data[7])
        self._lastRxTime = time.time()
        self._count += 1

    def get(self):
        if (time.time() - self._lastRxTime) > 5:
            self.value = str(0)
        return self.value

    @property
    def count(self):
        return self._count

    def get_count_string(self):
        return str(self._count)

    def get_last_rx_time(self):
        return self._lastRxTime
