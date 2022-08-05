from core import time

from .device import AntDevice, DeviceTypeID, Node


class Hall(AntDevice):
    def __init__(self, node: Node, sensor_id=0, device_type=DeviceTypeID.speed):
        super().__init__(node, sensor_id)

        self._device_type = device_type

        self._payload = None
        self._received_data = False
        self._last_data_read = None

        # TODO: add correnct circumference
        self._circumference = 1450
        self._cadence_circumference = 350

        # data store
        self._speed = 0
        self._cadence = 0
        self._distance = 0
        self._overall_distance = 0

        # attribute for data calculation
        self._last_speed_event_time = None
        self._current_speed_event_time = None

        self._last_cadence_event_time = 0
        self._current_cadence_event_time = 0

        self._last_speed_revolutions = None
        self._current_speed_revolutions = None

        self._last_cadence_revolutions = None
        self._current_cadence_revolutions = None

        # inizializzazione del channel ant
        self._init_channel()

    # NOTE: specializzazione metodi astratti di `AntReader`

    def _init_channel(self):
        if self._channel is None:
            self._channel = self._create_channel()

        # callbacks for data
        self._channel.on_broadcast_data = self._receive_new_data
        self._channel.on_burst_data = self._receive_new_data

        if self._device_type == DeviceTypeID.speed:
            self._channel.set_period(8118)
        elif self._device_type == DeviceTypeID.speed_cadence:
            self._channel.set_period(8086)
        else:
            raise ValueError(
                "The Type of the device doesn't match the supported ones (123, 121)"
            )

        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)
        self._channel.set_id(self._sensor_id, self._device_type.value, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        # callback for ant data

        self._payload = data
        self._received_data = True
        self._last_data_read = self._current_time()

    def _current_time(self):
        return time._unix_time()

    def _elapsed_time(self):
        return self._current_time() - self._last_data_read

    def _is_active(self):
        # is false only when no data has been yet received or not for 5s
        return self._last_data_read and self._elapsed_time() < 5

    def read_data(self) -> dict:
        if not self._is_active():
            self._speed = 0
            self._cadence = 0
            self._distance = 0
            self._overall_distance = 0

        elif self._received_data:
            self._received_data = False

            # freeze current reference
            self._current_speed_event_time = self._get_speed_event_time()
            self._current_speed_revolutions = self._get_speed_revolutions()
            self._current_cadence_event_time = self._get_cadence_event_time()
            self._current_cadence_revolutions = self._get_cadence_revolutions()

            self._speed = self.calculate_speed() or self._speed
            self._distance = self.calculate_distance() or 0
            self._overall_distance = round(self._overall_distance + self._distance, 4)

            if self._device_type is DeviceTypeID.speed_cadence:
                self._cadence = self.calculate_cadence() or self._cadence

            # update last reference
            self._last_speed_event_time = self._current_speed_event_time
            self._last_speed_revolutions = self._current_speed_revolutions
            self._last_cadence_event_time = self._current_cadence_event_time
            self._last_cadence_revolutions = self._current_cadence_revolutions

        return {
            "speed": self._speed,
            "distance": self._overall_distance,
            "cadence": self._cadence,
        }

    # NOTE: metodi propri della classe

    def _get_cadence_event_time(self):
        return self._payload[1] * 256 + self._payload[0]

    def _get_cadence_revolutions(self):
        return self._payload[3] * 256 + self._payload[2]

    def _get_speed_event_time(self):
        return self._payload[5] * 256 + self._payload[4]

    def _get_speed_revolutions(self):
        return self._payload[7] * 256 + self._payload[6]

    def _check_speed_register_overflow(self):
        if self._current_speed_event_time < self._last_speed_event_time:
            self._last_speed_event_time = self._current_speed_event_time

        if self._current_speed_revolutions < self._last_speed_revolutions:
            self._last_speed_revolutions = self._current_speed_revolutions

    def _check_cadence_register_overflow(self):
        if self._current_cadence_event_time < self._last_cadence_event_time:
            self._last_cadence_event_time = self._current_cadence_event_time

        if self._current_cadence_revolutions < self._last_cadence_revolutions:
            self._last_cadence_revolutions = self._current_cadence_revolutions

    def calculate_cadence(self):
        if (
            self._last_cadence_event_time is None
            or self._last_cadence_revolutions is None
        ):
            return None

        self._check_cadence_register_overflow()

        if self._current_cadence_event_time == self._last_cadence_event_time:
            return None

        return round(
            60
            * (self._current_cadence_revolutions - self._last_cadence_revolutions)
            * 1024
            / (self._current_cadence_event_time - self._last_cadence_event_time),
            4,
        )

        # TODO: check this formula
        # return round(
        #     3.6
        #     * (self._current_cadence_revolutions - self._last_cadence_revolutions)
        #     * 1.024
        #     * self._cadence_circumference
        #     / (self._current_cadence_event_time - self._last_cadence_event_time),
        #     4,
        # )

    def calculate_speed(self):
        if self._last_speed_event_time is None or self._last_speed_revolutions is None:
            return None

        self._check_speed_register_overflow()

        if self._current_speed_event_time == self._last_speed_event_time:
            return None

        return round(
            3.6
            * (self._current_speed_revolutions - self._last_speed_revolutions)
            * 1.024
            * self._circumference
            / (self._current_speed_event_time - self._last_speed_event_time),
            4,
        )

    def calculate_distance(self):
        # distance calculation depends on speed
        if self._last_speed_revolutions is None or self._last_speed_revolutions is None:
            return None

        self._check_speed_register_overflow()

        return round(
            self._circumference
            * (self._current_speed_revolutions - self._last_speed_revolutions)
            / 1000,
            2,
        )

    # def get_trap_speed(self):
    #     if self.trap_speed == 0:
    #         s = 0
    #         for elem in self.average_array:
    #             s += elem
    #         if len(self.average_array) > 0:
    #             self.trap_speed = s / len(self.average_array)
    #     return str(round(self.trap_speed, 2))

    # @property
    # def trap_info(self):
    #     # per il record dell'ora
    #     if self.settings.hour_record:
    #         if self.time_int == 0:
    #             return ""
    #         return "V_med: " + str(3.6 * self.distance / self.time_int)
    #     if self.distance < self.settings.run_length:
    #         return (
    #             "Trappola tra "
    #             + str(round(self.settings.run_length - self.distance))
    #             + " metri"
    #         )
    #     elif self.distance > self.settings.run_length and self.distance_trap >= 0:
    #         return "Fine trappola tra " + str(round(self.distance_trap)) + " metri"
    #     else:
    #         return "Velocità media trappola: " + str(self.get_trap_speed())
