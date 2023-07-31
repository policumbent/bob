from enum import Enum
from collections import deque
from math import pi
from typing import List

from .device import AntDevice, DeviceTypeID


class MessageType(Enum):
    # used
    calibration = 0x1
    power_only = 0x10
    crank_torque_freq = 0x20
    other = None

    # not used
    get_set_param = 0x2
    mesurement_output = 0x3
    torque_at_wheel = 0x11
    torque_at_crank = 0x12
    pedal_smoothness = 0x13
    right_force_angle = 0xE0
    left_force_angle = 0xE1
    pedal_position = 0xE2
    menifacturer_info = 0x50
    product_info = 0x51
    battery_voltage = 0x52


class Powermeter(AntDevice):
    def __init__(self, node, sensor_id=0, device_type=DeviceTypeID.powermeter):
        super().__init__(node, sensor_id)

        # device type
        self._device_type_id = device_type.value
        self._sensor_type = "powermeter"

        self._last_message_type = None

        # data store
        self._power = 0
        self._instant_power = 0
        self._cadence = 0
        self._power_buffer = deque(maxlen=5)

        # attributes for data calculation
        self._offset = 0
        self._offset_flag = True
        self._data_ready_collection = False # flag used to understand if data is new or not from other classes

        # attributes for Messagetype.crank_torque_freq
        self._slope = None
        self._torque = None

        self._torque_ticks = None
        self._torque_frequency = None
        self._cadence_period = None

        self._last_torque_ticks_stamp = None
        self._current_torque_ticks_stamp = None

        self._last_rotations_count = None
        self._current_rotations_count = None

        self._elapsed_time_interval = None

        self._last_rx_time = None
        self._current_rx_time = None

        # inizializzazione del channel ant
        self._init_channel()

    # Specializzazione metodi astratti di `AntReader`

    def _init_channel(self):
        if self._channel is None:
            self._channel = self._create_channel()

        # callbacks for data
        self._channel.on_broadcast_data = self._receive_new_data
        self._channel.on_burst_data = self._receive_new_data

        self._channel.set_period(8182)
        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        self._channel.set_id(self._sensor_id, self._device_type_id, 0)

        # open channel
        self._channel.open()
        # self._request_calibration()

    def _data_collected(self):
        self._data_ready_collection = False

    def _data_prepare(self):
        self._data_ready_collection = True

    def is_data_ready(self) -> bool:
        return    self._data_ready_collection

    def get_sensor_type(self):
        return self._sensor_type

    def _receive_new_data(self, data):
        # callback for ant data
        self._data_prepare()
        self._payload = data
        self._received_data = True
        self._last_message_type = self._get_message_type()
        # print(f"Received datas: {self._payload} type: {self._last_message_type}")
        self._last_data_read = self._current_time()

    def read_data(self) -> dict:
        # if the 
        if not self._is_active():
            self._power = 0
            self._cadence = 0
            self._power_buffer.clear()
            self._offset_buffer.clear()

        elif self._received_data and self._last_message_type is MessageType.power_only:
            self._cadence = self._get_instant_cadence()
            self._instant_power = self._get_instant_power()
            if(self._instant_power is not None and self._instant_power != 0.0):
                self._power_buffer.append(self._instant_power)

            if(len(self._power_buffer) >0):
                self._power = round(
                    sum((self._power_buffer)) / len(self._power_buffer)
                )

            # TODO: provare con srm cerberus
            # print(self._get_accumulated_power())

        elif (
            self._received_data
            and self._last_message_type is MessageType.crank_torque_freq
        ):
            # self._offset_flag = False
            # parameters to set before proceeding with computations retrieved from payload
            self._slope = self._get_slope()
            self._current_rx_time = self._get_timestamp()
            self._current_rotations_count = self._get_rotations_count()
            self._current_torque_ticks_stamp = self._get_torque_ticks_stamp()

            # intermediate calculations
            self._elapsed_time_interval = self._calculate_elapsed_time()
            self._cadence_period = self._calculate_cadence_period()
            self._torque_ticks = self._calculate_torque_ticks()
            self._torque_frequency = self._calculate_torque_frequency()
            self._torque = self._calculate_torque()

            # calculate the average power
            self._instant_power = self._calculate_power()
            if self._instant_power is not None and self._instant_power != 0.0:
                self._power_buffer.append(self._instant_power)
            
            if(len(self._power_buffer) >0):
                self._power = round(
                    sum((self._power_buffer)) / len(self._power_buffer)
                )

            self._cadence = self._calculate_cadence() or self._cadence

            # storing previous parameter results
            self._last_rx_time = self._current_rx_time
            self._last_rotations_count = self._current_rotations_count
            self._last_torque_ticks_stamp = self._current_torque_ticks_stamp

        elif self._received_data and self._last_message_type is MessageType.calibration and self._offset_flag:
            self._offset = self._get_offset()
            self._offset_flag = False

        if self._received_data:
            # print(f"Offset {self._offset}, Cadence {self._cadence}, Power {self._power}, Torque ticks {self._torque_ticks}, Torque frequency {self._torque_frequency}, Elapsed Time {self._elapsed_time_interval}")
            self._received_data = False

        # the data has been collected --> will be restored by next callback
        self._data_collected()
        return {
            "timestamp": str(self._last_data_read),
            "power": float(self._power),
            "instant_power": float(self._instant_power),
            "cadence": float(self._cadence)
        }

    # Metodi propri della classe

    def _is_buffer_full(self, buffer: deque):
        if buffer.maxlen is None:
            return False

        return len(buffer) == buffer.maxlen

    def _get_message_type(self):
        try:
            return MessageType(self._payload[0])
        except:
            return MessageType.other

    # Metodi per MessageType.calibration

    def _get_offset(self):
        return self._combine_bin(self._payload[7], self._payload[6])

    # Metodi per MessageType.power_only

    def _get_instant_cadence(self):
        return self._payload[3]

    def _get_accumulated_power(self):
        return self._combine_bin(self._payload[4], self._payload[5])

    def _get_instant_power(self):
        return self._combine_bin(self._payload[6], self._payload[7])

    # Metodi per MessageType.crank_torque_freq

    def _check_rotation_register_overflow(self):
        if self._last_rotations_count > self._current_rotations_count:
            self._last_rotations_count = self._last_rotations_count - 256

    def _check_slope_register_overflow(self):
        if self._slope < 100 or self._slope > 500:
            self._slope = 0

    def _check_rx_time_register_overflow(self):
        if self._last_rx_time > self._current_rx_time:
            self._last_rx_time = self._last_rx_time - 65536

    def _check_torque_ticks_register_overflow(self):
        if self._last_torque_ticks_stamp > self._current_torque_ticks_stamp:
            self._last_torque_ticks_stamp = self._last_torque_ticks_stamp - 65536

    def _get_rotations_count(self):
        return self._payload[1]

    def _get_slope(self):
        return self._combine_bin(self._payload[3], self._payload[2])

    def _get_timestamp(self):
        return self._combine_bin(self._payload[5], self._payload[4])

    def _get_torque_ticks_stamp(self):
        return self._combine_bin(self._payload[7], self._payload[6])

    def _calculate_elapsed_time(self):
        if self._last_rx_time is None or self._current_rx_time is None:
            return None

        self._check_rx_time_register_overflow()

        return (self._current_rx_time - self._last_rx_time) * 0.0005

    def _calculate_cadence_period(self):
        if (
            self._elapsed_time_interval is None
            or self._current_rotations_count is None
            or self._last_rotations_count is None
        ):
            return None

        self._check_rotation_register_overflow()

        if self._current_rotations_count == self._last_rotations_count:
            return None

        return self._elapsed_time_interval / (
            self._current_rotations_count - self._last_rotations_count
        )

    def _calculate_torque_ticks(self):
        if (
            self._current_torque_ticks_stamp is None
            or self._last_torque_ticks_stamp is None
        ):
            return None

        self._check_torque_ticks_register_overflow()

        return self._current_torque_ticks_stamp - self._last_torque_ticks_stamp

    def _calculate_torque_frequency(self):
        if self._torque_ticks is None or self._elapsed_time_interval is None:
            return None

        # self._check_torque_ticks_register_overflow()

        if self._elapsed_time_interval == 0 or self._torque_ticks == 0:
            return None

        return (1 / float(self._elapsed_time_interval / self._torque_ticks)) - self._offset

    def _calculate_torque(self):
        if self._torque_frequency is None or self._slope is None:
            return None

        self._check_slope_register_overflow()

        if self._slope == 0:
            return None

        return self._torque_frequency / (self._slope / 10)

    def _calculate_cadence(self):
        # here the return is zero, otherwise we may influence the final data
        if self._cadence_period is None:
            return 0

        if self._cadence_period == 0:
            return 0

        return round(60 / self._cadence_period, 4)

    def _calculate_power(self):
        # here the return is zero, otherwise we may influence the final data
        if self._torque is None or self._cadence is None:
            return 0

        return self._torque * self._cadence * pi / 30

    def _request_calibration(self):
        cal_request = [0xAA, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self._channel.send_broadcast_data(cal_request)
