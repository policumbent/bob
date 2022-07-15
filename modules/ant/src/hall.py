import time
from core.message import Message, MexType, MexPriority
from collections import deque

from .reader import AntReader, Node, Channel

# CIRCUMFERENCE = 1.450
from .settings import Settings


class Hall(AntReader):
    _DEVICE_TYPE_ID = 121

    def __init__(self, node: Node, id: int):
        super().__init__(node, id)

        self._speed = 0.0
        self.__time_int = 0
        # self._send_message = send_message
        # self._settings = settings
        # self._settings_lock = threading.Lock()
        self._state = False

        self.count = 0
        self.count2 = 0
        self.trap_count = 0
        self.lastTime = -1
        self.lastRevolutions = -1
        self.lastRxTime = time.time()
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

        self._channel.set_period(8085)
        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        # 121 -> DEVICE ID of VEL/CADsensor
        # Taurus id -> 8142

        # speed_sensor_id = self._settings.speed_sensor_id
        self._channel.set_id(self._sensor_id, self._DEVICE_TYPE_ID, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        self.data = data
        self.newData = True
        self.count += 1

    def read_data(self) -> dict:
        self._state = True

        if self.newData:
            self.count2 += 1
            # t1 = time.time()
            self.newData = False
            # print('>>> dentro __run')
            self.calculate_speed(self.data)

        return self._speed

    # NOTE: metodi propri della classe

    # def signal(self, value: str):
    #     if value == "reset":
    #         self.reset_distance()

    # def update_settings(self, settings: Settings):
    #     with self._settings_lock:
    #         self._settings = settings

    # def export(self):
    #     return {"speed": round(self.speed, 2), "distance": round(self.distance, 2)}

    # TODO: DEPRECATE
    #    def _run(self):
    #        self._state = True
    #        while True:
    #            with self._settings_lock:
    #                if self.newData:
    #                    self.count2 += 1
    #                    # t1 = time.time()
    #                    self.newData = False
    #                    # print('>>> dentro __run')
    #                    self.calculate_speed(self.data)
    #                self.distance_trap = self.settings.run_length +\
    #                    self.settings.trap_length - self.distance
    #                if self.distance > self.settings.run_length and self.distance_trap >= 0:
    #                    self.average_array.append(self.speed)
    #                if self.trap_count == 0:
    #                    self._send_message(Message(self.trap_info, MexPriority.medium, MexType.trap, 1, 1))
    #                self.trap_count = (self.trap_count + 1) % 10
    #            time.sleep(0.1)

    def running(self):
        self._state = True

        if self.newData:
            self.count2 += 1
            # t1 = time.time()
            self.newData = False
            # print('>>> dentro __run')
            self.calculate_speed(self.data)

        # TODO: il calcolo della distanza dalla trappolla va fatto direttamente
        #       nel modulo `video` tramite il dato della distanza percorsa
        # self.distance_trap = (
        #     self.settings.run_length + self.settings.trap_length - self.distance
        # )

        if self.distance > self.settings.run_length and self.distance_trap >= 0:
            self.average_array.append(self.speed)

        # if self.trap_count == 0:
        #     self._send_message(
        #         Message(self.trap_info, MexPriority.medium, MexType.trap, 1, 1)
        #     )

        # self.trap_count = (self.trap_count + 1) % 10

    @property
    def speed(self):
        if (time.time() - self.lastRxTime) > 5:
            self._speed = 0
        return self._speed

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, s):
        self._settings = s

    @property
    def time_int(self) -> int:
        return self.__time_int

    @time_int.setter
    def time_int(self, time_int: int):
        self.__time_int = time_int

    # TODO: DEPRECATE
    def set_channel(self, channel_cad_vel: Channel):
        """
        Function used to set the channel velocity and cadence

        :param channel_cad_vel = chanel for velocity and cadence
        """

        channel_cad_vel.on_broadcast_data = self.on_data_cadence_speed
        channel_cad_vel.on_burst_data = self.on_data_cadence_speed
        channel_cad_vel.set_period(8086)
        # 240 seconds to get the signal from the sensor
        channel_cad_vel.set_search_timeout(255)
        channel_cad_vel.set_rf_freq(57)

        # 121 -> DEVICE ID of VEL/CADsensor
        # Taurus id -> 8142

        #        with self._settings_lock:
        #            speed_sensor_id = self._settings.speed_sensor_id

        speed_sensor_id = self._settings.speed_sensor_id
        channel_cad_vel.set_id(speed_sensor_id, 121, 0)

    # TODO: DEPRECATE
    def on_data_cadence_speed(self, data):
        # print('>>> new speed')
        self.data = data
        self.newData = True
        self.count += 1

    def calculate_speed(self, data):
        """
        Computes the speed of the bike by calculating the number of rotations of the wheels.
        :param data = the data array, used to calculate the speed of the bike
        """

        # if (data[0] == 5):
        #     print ("data[0] == 5")
        #     return
        event_time = data[5] * 256 + data[4]

        if event_time == self.lastTime:
            return

        revolutions = data[7] * 256 + data[6]
        self.calc_speed(event_time, revolutions)
        # print ("Speed "+ self._speed)
        self.lastRxTime = time.time()
        self.lastTime = event_time
        self.lastRevolutions = revolutions
        self.count2 += 1

    def calc_speed(self, event_time, revolutions):
        # print ("Calcolo vel")
        if self.lastTime == -1:
            return 0
        if event_time < self.lastTime:
            event_time += 64 * 1024
        if revolutions < self.lastRevolutions:
            revolutions += 65535

        # TODO: 2200 mm is the diameter of the wheel, retrive it from config

        self.distance += 2200 * (revolutions - self.lastRevolutions) / 1000

        self._speed = (
            3.6
            * (revolutions - self.lastRevolutions)
            * 1.024
            * 2200
            / (event_time - self.lastTime)
        )

    def get(self):
        if (time.time() - self.lastRxTime) > 5:
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
