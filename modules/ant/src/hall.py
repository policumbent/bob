from core.message import Message, MexType, MexPriority
from core import time
from collections import deque

from .device import AntDevice, DeviceTypeID, Node, Channel

# CIRCUMFERENCE = 1.450
# from .settings import Settings


class Hall(AntDevice):
    def __init__(self, node: Node, sensor_id=0, device_type=DeviceTypeID.speed):
        super().__init__(node, sensor_id)

        self._device_type = device_type

        self._speed = 0.0
        self._cadence = 0.0
        self.__time_int = 0
        # self._settings = Settings()

        # self._send_message = send_message
        # self._settings = settings
        # self._settings_lock = threading.Lock()
        self._state = False

        self.count = 0
        self.count2 = 0
        self.trap_count = 0
        self.last_wheel_revolutions = -1
        self.last_pedal_revolutions = -1
        self.last_event_time = -1  # TIME of the last occurrence of an event registered by sensor
        self.last_speed_measure_time = self._current_time()  # TIME of last registration of speed
        self.last_data_read = None
        self.distance = 0
        self.data = None
        self.newData = False
        self.distance_to_go = 0
        self.distance_trap = 0
        self.average_array = deque()
        self.trap_speed = 0

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
            raise ValueError("The Type of the device doesn't match the supported ones (123, 121)")


        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        # 121 -> DEVICE ID of VEL/CADsensor
        # Taurus id -> 8142

        # speed_sensor_id = self._settings.speed_sensor_id
        self._channel.set_id(self._sensor_id, self._device_type.value, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        # Function used to signal the receiving of new data
        self.data = data
        self.newData = True
        self.count += 1
        self.last_data_read = self._current_time()

    def _current_time(self):
        return time._unix_time()

    def _elapsed_time(self):
        return self._current_time() - self.last_data_read

    def _is_active(self):
        # is false only when no data has been yet received or not for 5s
        return self.last_data_read and self._elapsed_time() < 10


    def read_data(self) -> dict:
        self._state = True

        # when new data is available, use it to calculate the speed
        # the speed is calculated periodically in running
        if self.newData:
            self.count2 += 1
            # t1 = time.time()
            self.newData = False
            # print('>>> dentro __run')
            self.calculate_speed(self.data)
            if self._device_type == DeviceTypeID.speed_cadence:
                self.calculate_cadence(self.data)
        elif not self._is_active():
            return None  # if you did not receive data for the last 5s then it is out(unless Newdata is true)

        if self._device_type == DeviceTypeID.speed:
            self._data = self._speed
            return {
                    "speed": self._data
                    }
        elif self._device_type == DeviceTypeID.speed_cadence:
            self._data = self._speed, self._cadence
            return {
                "speed": self._data[0],
                "cadence": self._data[1]
            }

        # if the sensor is not recognized then it returns None
        return None

    # NOTE: metodi propri della classe

    def calculate_cadence(self, data):
        """
        Computes the cadence of the biker by calculating the number of rotations of the pedals.
        :param data = the data array, used to calculate the speed of the bike
        """
        event_time = data[5] * 256 + data[4]

        # hypothetical situation(not actually real)
        if event_time == self.last_event_time:
            return

        revolutions_pedal = data[3] * 256 + data[2]

        self.calc_cadence_from_revolutions(event_time, revolutions_pedal)
        self.last_pedal_revolutions = revolutions_pedal


    def calculate_speed(self, data):
        """
        Computes the speed of the bike by calculating the number of rotations of the wheels.
        :param data = the data array, used to calculate the speed of the bike
        """

        # if (data[0] == 5):
        #     print ("data[0] == 5")
        #     return
        event_time = data[5] * 256 + data[4]

        # hypothetical situation(not actually real)
        if event_time == self.last_event_time:
            return

        revolutions_wheel = data[7] * 256 + data[6]
        self.calc_speed_form_revolutions(event_time, revolutions_wheel)
        # print ("Speed "+ self._speed)
        self.last_speed_measure_time = self._current_time()
        self.last_event_time = event_time
        self.last_wheel_revolutions = revolutions_wheel
        self.count2 += 1

    def calc_speed_form_revolutions(self, event_time, revolutions):
        # print ("Calcolo vel")
        if self.last_event_time == -1:
            return 0

        # these checks manage sensor register overflow (16 bits = 65535 states)
        if event_time < self.last_event_time:
            event_time += 65536
        if revolutions < self.last_wheel_revolutions:
            revolutions += 65535

        # NOTE: per adesso circonferenza hardcoded (sigh)
        circumference = 1.450

        # NOTE: per adesso niente distanza (sigh)

        # self.distance += circumference * (revolutions - self.last_wheel_revolutions) / 1000

        # whe must do the check as soon as possible
        # if self.distance > self.settings.run_length and self.distance_trap >= 0:
        #     self.average_array.append(self.speed)


        # TODO: indagare velocità scalata di 1000
        self._speed = (
            3.6
            * (revolutions - self.last_wheel_revolutions)
            * 1.024
            * circumference
            / (event_time - self.last_event_time)
        )*1000

    def calc_cadence_from_revolutions(self, event_time, revolutions):
        if self.last_event_time == -1:
            return 0

        # these checks manage sensor register overflow (16 bits = 65535 states)
        if event_time < self.last_event_time:
            event_time += 65536
        if revolutions < self.last_wheel_revolutions:
            revolutions += 65535

        self._cadence = (
            3.6
            * (revolutions - self.last_wheel_revolutions)
            * 1.024
            * 350  # self._settings.pedal_circumference. Now I have considered 175mm pedal length
            / (event_time - self.last_event_time)
        )


    def get(self):
        if (self._current_time() - self.last_speed_measure_time) > 5:
            self._speed = 0
        return str(round(self._speed, 1))

    def get_distance(self):
        return str(round(self.distance / 1000, 2))

    def set_distance(self, distance):
        self.distance = distance

    def get_count(self):
        return self.count

    def get_count_string(self):
        return str(self.count)

    def reset_distance(self):
        self.distance = 0
        self.average_array.clear()
        self.trap_speed = 0

    def get_trap_speed(self):
        if self.trap_speed == 0:
            s = 0
            for elem in self.average_array:
                s += elem
            if len(self.average_array) > 0:
                self.trap_speed = s / len(self.average_array)
        return str(round(self.trap_speed, 2))

    @property
    def trap_info(self):
        # per il record dell'ora
        if self.settings.hour_record:
            if self.time_int == 0:
                return ""
            return "V_med: " + str(3.6 * self.distance / self.time_int)
        if self.distance < self.settings.run_length:
            return (
                "Trappola tra "
                + str(round(self.settings.run_length - self.distance))
                + " metri"
            )
        elif self.distance > self.settings.run_length and self.distance_trap >= 0:
            return "Fine trappola tra " + str(round(self.distance_trap)) + " metri"
        else:
            return "Velocità media trappola: " + str(self.get_trap_speed())
