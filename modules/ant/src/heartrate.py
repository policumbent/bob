from .device import AntDevice, DeviceTypeID, Node

from core import time


class HeartRate(AntDevice):
    def __init__(
        self, node: Node, sensor_id = 0, device_type=DeviceTypeID.heartrate
    ):
        super().__init__(node, sensor_id)

        self._device_type_id = device_type.value
        self._last_data_time = None

        # inizializzazione del channel ant
        self._init_channel()

    # NOTE: specializzazione metodi astratti di `AntDevice`

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
        self._channel.set_id(self._sensor_id, self._device_type_id, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        self._data = data[7]
        self._last_data_time = self._current_time()

    def read_data(self) -> dict:
        if not self._is_active():
            return None

        return {"heartrate": self._data}

    # NOTE: metodi propri della classe

    def _current_time(self):
        return time._unix_time()

    def _elapsed_time(self):
        return self._current_time() - self._last_data_time

    def _is_active(self):
        return self._last_data_time and self._elapsed_time() < 5
