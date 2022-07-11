from .reader import AntReader, Node
from .ant.easy.channel import Channel
import time

from core.sensor import Sensor
from .settings import Settings


class HeartRate(AntReader):
    _DEVICE_TYPE_ID = 120

    def __init__(self, node: Node, id: int):
        super().__init__(node, id)

        self._value = -1
        self._state = False
        # self._settings = settings
        self._lastRxTime = time.time()
        self._count = 0

        # inizializzazione del channel ant
        self._init_channel()

    # NOTE: specializzazione metodi astratti di `AntReader`

    def _init_channel(self):
        if self._channel is None:
            self._channel = self._create_channel()

        # callbacks for data
        self._channel.on_broadcast_data = self._receive_new_data
        self._channel.on_burst_data = self._receive_new_data

        self._channel.set_period(8070)
        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        # 69  -> ID DELLA MIA FASCIA CARDIO, METTERE 0 PER TUTTE LE FASCIE
        # 120 -> DEVICE ID DEL SENSORE DELLA FC

        # hr_sensor_id = self._settings.hr_sensor_id
        self._channel.set_id(self._sensor_id, self._DEVICE_TYPE_ID, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        self._state = True
        self.value = int(data[7])
        self._lastRxTime = time.time()
        self._count += 1
        # print(self._lastRxTime)

    def read_data() -> dict:
        pass

    # NOTE: metodi propri della classe

    # def signal(self, value: str):
    #     pass

    # def update_settings(self, settings: Settings):
    #     pass

    @property
    def state(self):
        return self._state

    @property
    def value(self):
        if (time.time() - self._lastRxTime) > 5:
            self._value = 0
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    # TODO: DEPRECATE
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

    # TODO: DEPRECATE
    def on_data_heartrate(self, data):
        self._state = True
        self.value = int(data[7])
        self._lastRxTime = time.time()
        self._count += 1
        print(self._lastRxTime)

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
