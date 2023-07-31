from .device import AntDevice, DeviceTypeID, Node

from time import time


class HeartRate(AntDevice):
    def __init__(self, node: Node, sensor_id=0, device_type=DeviceTypeID.heartrate):
        super().__init__(node, sensor_id)

        self._device_type_id = device_type.value
        self._sensor_type="heartrate"

        # data store
        self._heartrate = 0

        self._data_ready_collection = False # flag used to understand if data is new or not from other classes

        # inizializzazione del channel ant
        self._init_channel()

    # Specializzazione metodi astratti di `AntDevice`

    def _init_channel(self):
        if self._channel is None:
            self._channel = self._create_channel()

        # callbacks for data
        self._channel.on_broadcast_data = self._receive_new_data
        self._channel.on_burst_data = self._receive_new_data

        self._channel.set_period(8070)
        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        self._channel.set_id(self._sensor_id, self._device_type_id, 0)

        # open channel
        self._channel.open()


    def _data_collected(self):
        self._data_ready_collection = False

    def _data_prepare(self):
        self._data_ready_collection = True

    def is_data_ready(self) -> bool:
        return    self._data_ready_collection

    def get_sensor_type(self):
        return self._sensor_type

    def _receive_new_data(self, data):
        self._data_prepare()
        self._payload = data
        self._last_data_read = self._current_time()

    def read_data(self) -> dict:
        self._heartrate = self._get_heartrate() if self._is_active() else 0
        self._data_collected()
        return {
            "timestamp": str(self._last_data_read),
            "heartrate": float(self._heartrate)
        }

    def get_sensor_type(self) -> str:
        return self._sensor_type

    # Metodi propri della classe

    def _get_heartrate(self):
        return self._payload[7]
