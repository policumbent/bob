from enum import Enum
from collections import deque
from math import pi

from .device import AntDevice, DeviceTypeID


class MessageType(Enum):
    calibration = 0x1
    get_set_param = 0x2
    mesurement_output = 0x3
    power_only = 0x10
    torque_at_wheel = 0x11
    torque_at_crank = 0x12
    pedal_smoothness = 0x13
    crank_torque_freq = 0x20
    right_force_angle = 0xE0
    left_force_angle = 0xE1
    pedal_position = 0xE2
    menifacturer_info = 0x50
    product_info = 0x51
    battery_voltage = 0x52
    other = None


# CHANNEL_PERIOD_VAL = 32768/MESSAGE_RATE(HZ)
# MESSAGE_RATE = 32768/32768 = 32768/8182 = 4HZ
# TEMPO_PER_LA_MEDIA = 3s
# LUNGHEZZA_VETTORE_MEDIA = TEMPO_PER_LA_MEDIA * MESSAGE_RATE = 4 * 3
# POTENZA MEDIA: 1s -> 4 || 3s -> 12 || 5s -> 20 || 10s --> 40 (impostare il valore desiderato)


class Powermeter(AntDevice):
    def __init__(self, node, sensor_id=0, device_type=DeviceTypeID.powermeter):
        super().__init__(node, sensor_id)

        # device type
        self._device_type_id = device_type.value

        self._last_message_type = None

        # data store
        self._power = 0
        self._cadence = 0

        # attribute for data calculation
        self._offset = 0

        # attributes for Messagetype.crank_torque_freq
        # they are initially set to None to simplify exception handling
        self._slope = None
        self._torque = None

        self._torque_frequency = None
        self._torque_ticks = None
        self._previous_torque_ticks_stamp = None
        self._current_torque_ticks_stamp = None

        self._cadence_period = None

        self._previous_rotations_count = None
        self._current_rotations_count = None

        self._elapsed_time_interval = None
        self._last_rx_time = None
        self._current_rx_time = None

        # attributes for Messagetype.poweronly
        self._power_buffer = deque(maxlen=5)

        # attributes for Messagetype.calibration
        self._offset_buffer = deque(maxlen=10)


        # lunghezza_vettore_media = settings.average_power_time * 4
        # lunghezza_vettore_media_1s = 4

        # self._power: int = 0
        # self._calibration_value = 0
        # self._calibration = False
        # self._state = False
        # self._settings = settings

        # self.count = 0
        # self.count2 = 0
        # self._cadence = 0
        # self.eventEquals = 0
        # self.n_average = 10
        # self.timeStampP = 0
        # self.eventCountP = 0
        # self.torqueTicksStampP = 0

        # # self.offset = 500  # 495
        # self.calibration_count = 0
        # # self.send_message = send_message
        # self.lastRxTime = time.time()
        # self.newData = False
        # self.data = None
        # self.torque = 0  # type: float
        # self.averagePower = 0
        # self.averagePower1s: int = 0
        # self.count3 = 1
        # self.lastAverageTime = 0
        # self.lastAverageTime1s = 0
        # # self.average_array = deque(lunghezza_vettore_media * [0])
        # # self.average_array_1s = deque(lunghezza_vettore_media_1s * [0])
        # self._last_rx = time.time()

        # self._calibration_lock = threading.Lock()
        # self._worker_thread = Thread(target=self._run, daemon=True)
        # self._worker_thread.start()

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

    def _receive_new_data(self, data):
        # callback for ant data

        self._payload = data
        self._received_data = True
        self._last_data_read = self._current_time()
        self._last_message_type = self._get_message_type()

    def read_data(self) -> dict:
        if not self._is_active(10):
            self._power = 0
            self._cadence = 0
            self._offset = 0

        elif self._received_data and self._last_message_type is MessageType.power_only:
            self._cadence = self._get_instant_cadence()
            self._power_buffer.append(self._get_instant_power())

            # if buffer is full enaugh calculate average value of power
            if self._is_buffer_full(self._power_buffer):
                self._power = round(
                    sum((self._power_buffer)) / self._power_buffer.maxlen, 4
                )

            # TODO: provare con srm cerberus
            # print(self._get_accumulated_power())

        elif self._received_data and self._last_message_type is MessageType.crank_torque_freq:

            # parameters to set before proceeding with computations -- retrieve from payload
            self._current_rotations_count = self._get_rotations_count()
            self._slope = self._get_slope()
            self._current_rx_time = self._get_timestamp()
            self._current_torque_ticks_stamp = self._get_torque_ticks_stamp()

            # intermediate calculations
            self._elapsed_time_interval = self.calculate_elapsed_time()
            self._cadence_period = self.calculate_cadence_period()
            self._torque_ticks = self.calculate_torque_ticks()
            self._torque_frequency = self.calculate_torque_frequency()
            self._torque = self.calculate_torque()

            # calculations necessary for the cadence
            self._cadence = self.calculate_cadence()
            self._power = self.calculate_power()

            # storing previous parameter results
            self._previous_rotations_count = self._current_rotations_count
            self._last_rx_time = self._current_rx_time
            self._previous_torque_ticks_stamp = self._current_torque_ticks_stamp

        elif self._received_data and self._last_message_type is MessageType.calibration:
            self._offset_buffer.append(self._get_offset())

            if self._is_buffer_full(self._offset_buffer):
                self._offset = round(
                    sum(self._offset_buffer) / self._offset_buffer.maxlen
                )

            # print(self._offset)

        return {"power": self._power, "cadence": self._cadence}

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
    # getters
    def _get_rotations_count(self):
        return self._payload[1]

    def _get_slope(self):
        return self._combine_bin(self._payload[3], self._payload[2])

    def _get_timestamp(self):
        return self._combine_bin(self._payload[5], self._payload[6])

    def _get_torque_ticks_stamp(self):
        return self._combine_bin(self._payload[7], self._payload[6])

    # calculations
    def calculate_cadence_period(self):
        if self._elapsed_time_interval is None:
            return None
        if self._current_rotations_count - self._previous_rotations_count == 0:
            return None
        return self._elapsed_time_interval / (
                    self._current_rotations_count - self._previous_rotations_count)

    def calculate_cadence(self):
        if self._cadence_period is None:
            return None
        return round(60 / self._cadence_period)

    def calculate_elapsed_time(self):
        if self._last_rx_time is None or self._current_rx_time is None:
            return None
        return (self._current_rx_time - self._last_rx_time) * 0.0005

    def calculate_power(self):
        if self._torque is None or self._cadence is None:
            return None
        return self._torque * self._cadence * pi / 30

    def calculate_torque_ticks(self):
        if self._current_torque_ticks_stamp is None or self._previous_torque_ticks_stamp is None:
            return None
        return self._current_torque_ticks_stamp - self._previous_torque_ticks_stamp

    def calculate_torque_frequency(self):
        if self._torque_ticks is None or self._elapsed_time_interval is None:
            return None
        return self._torque_ticks / self._elapsed_time_interval - self._offset

    def calculate_torque(self):
        if self._torque_frequency is None:
            return None
        return self._torque_frequency * 10 / self._slope



    # TODO: DEPRECATE
    # def _run(self):
    #     self._state = True
    #     while True:
    #         if self.newData:
    #             self.count2 += 1
    #             self.newData = False
    #             self.calculatePower(self.data)

    #         if (time.time() - self.lastRxTime) > 4:
    #             self._power = 0
    #             self.count3 = 1
    #             # print(self.count3)
    #         self.calculate_average_power()
    #         self.calculateAveragePower1s()

    #         if self.calibration:
    #             self.calibration_count = 10
    #             self.calibration = False

    #         time.sleep(0.1)

    # print("AVERAGE: ", self.getAverage())
    # print("POW1S: ", self.get_average_1s_str())
    # print("POW3S: ", self.getAverage())
    # print("POWER: ", self.get())

    # 0 -> 0x20 potenza / 0x10 calibrazione
    # 1 -> Update Event Count -> Rotation event counter increments with each completed pedal revolution.
    # Range: 256
    # 2 -> Slope MSB -> Slope defines the variation of the output frequency.
    # 3 -> Slope LSB -> Units: 1/10Nm/Hz  Range: 100 - 500
    # 4 -> Time Stamp MSB -> Time of most recent rotation event
    # 5 -> Time Stamp LSB -> Units: 1/2000s  Range: 32.7s
    # 6 -> Torque Ticks Stamp MSB -> Count of most recent torque event
    # 7 -> Torque Ticks Stamp LSB -> Range: 65536 ticks

    # def calculate_average_power(self):
    #     if (time.time() - self.lastAverageTime) < 0.25:
    #         return
    #     self.average_array.appendleft(self.value)
    #     self.average_array.pop()
    #     somma = 0
    #     for elem in self.average_array:
    #         somma += elem
    #     self.lastAverageTime = time.time()
    #     self.averagePower = somma / len(self.average_array)

    # def calculateAveragePower1s(self):
    #     if (time.time() - self.lastAverageTime1s) < 0.25:
    #         return
    #     self.average_array_1s.appendleft(self.value)
    #     self.average_array_1s.pop()
    #     somma = 0
    #     for elem in self.average_array_1s:
    #         somma += elem
    #     self.lastAverageTime1s = time.time()
    #     self.averagePower1s = somma / len(self.average_array_1s)

    # def calculatePower(self, data):
    #     if data[0] == 1:
    #         # print ("Offset attuale: "+ str(offset)+" Offset salvato: "+ str(self.offset))
    #         # todo: da testare il meccanismo di calibrazione
    #         if self.calibration_count > 0:
    #             self._calibration_value = (data[6] << 8) + data[7]
    #             # todo: se io mostro un messaggio per un secondo e i pacchetti arrivano con una frequenza maggiore
    #             # non avrò dati aggiornati a schermo per la calibrazione, bisogna inventarsi qualcosa
    #             # self.mex.set("Calibrazione tra " +
    #             #              str(self.calibrazione) + "pacchetti", 3, 1)
    #             # self.send_message(Message("NON TOCCARE - " + str(self._calibration_value),
    #             #                           MexPriority.medium, MexType.default, 1, 1))
    #             self.calibration_count -= 1
    #             return

    #         if self.calibration_count == 0:
    #             # todo: verificare che lo shift riporti un risultato giusto pure qui
    #             self._calibration_value = (data[6] << 8) + data[7]
    #             # print("CALIBRAZIONE ", self._calibration_value)
    #             # self.send_message(Message("Calibrato a " + str(self._calibration_value),
    #             #                           MexPriority.medium, MexType.default, 5, 10))
    #             #                state.update("calibration_value": offset)
    #             #                 Settings.save()
    #             #                 Settings.settings_request = True
    #             self.calibration_count -= 1
    #             return

    #     if data[0] == 32:
    #         event_count = data[1]
    #         slope = (data[2] << 8) + data[3]
    #         timeStamp = (data[4] << 8) + data[5]
    #         torqueTicksStamp = (data[6] << 8) + data[7]

    #         if event_count == self.eventCountP:
    #             self.eventEquals += 1
    #             return
    #         else:
    #             self.eventEquals = 0
    #         # if (data[0] != 32):
    #         #     return
    #         # ## CALCOLO CADENZA
    #         # # periodoCadenza = (timeStamp - timeStampP) x 0.0005 / (event_count - eventCountP)
    #         # # cadenza = round(60/periodoCadenza)
    #         # print (str(event_count) + " " + str(self.eventCountP))
    #         eventCountC = event_count - self.eventCountP
    #         if eventCountC < 0:
    #             eventCountC = event_count - self.eventCountP + 256

    #         deltaTime = timeStamp - self.timeStampP
    #         if deltaTime < 0:
    #             deltaTime += 65535
    #         if deltaTime == 0:
    #             deltaTime = 0.000001

    #         cadencePeriod = deltaTime * 0.0005 / eventCountC
    #         if cadencePeriod != 0:
    #             cadence = 60 / cadencePeriod
    #             self.cadence = round(cadence)
    #         else:
    #             cadence = 1
    #         # ## CALCOLO POTENZA
    #         # print (data[0])
    #         elapsedTime = deltaTime * 0.0005
    #         torqueTicks = torqueTicksStamp - self.torqueTicksStampP
    #         if torqueTicks == 0:
    #             torqueTicks = 0.0000001
    #         if torqueTicks < 0:
    #             torqueTicks += 65536

    #         torqueFrequency = (
    #             1 / (elapsedTime / torqueTicks)
    #         ) - self._calibration_value
    #         #    torqueFrequency = 1
    #         #    print ("Slope: " + str(slope))
    #         torque = torqueFrequency / (slope / 10.0)
    #         #    print ("torque: " + str(torque))
    #         power = torque * cadence * 3.1415 / 30
    #         # print ("deltaTime: " + str(deltaTime))
    #         # print ("TorqueTicks: " + str(torqueTicks))
    #         # print ("elapsedTime: " + str(elapsedTime))
    #         # print ("torqueFrequency: " + str(torqueFrequency))
    #         # print ("power: " + str(power))
    #         # power =(100*torque * float(self.cadence) * 3.1415 / 30.0)
    #         if self.count3 >= 0:
    #             power = 0
    #             self.count3 -= 1
    #         self._power = power
    #         self.torque = torque
    #         self.timeStampP = timeStamp
    #         self.eventCountP = event_count
    #         self.torqueTicksStampP = torqueTicksStamp
    #         self.lastRxTime = time.time()

    # def getCadence(self):
    #     if (time.time() - self.lastRxTime) > 4:
    #         self.cadence = 0
    #     if self.eventEquals >= 12:
    #         self.cadence = 0
    #     return self.cadence

    # def get(self) -> int:
    #     if self.eventEquals >= 12:
    #         self._power = 0
    #     return round(self._power)

    # def get_count(self):
    #     return self.count2

    # def getAverage(self) -> int:
    #     if self.averagePower is None:
    #         return 0
    #     return round(self.averagePower)

    # def get_average_1s_str(self) -> int:
    #     if self.averagePower1s is None:
    #         return 0
    #     return round(self.averagePower1s)

    # def get_average_1s(self) -> int:
    #     if self.averagePower1s is None:
    #         return 0
    #     return round(self.averagePower1s)

    # def getCountString(self):
    #     return str(self.get_count())

    # def getTorque(self):
    #     if (time.time() - self.lastRxTime) > 4:
    #         self.torque = 0
    #     if self.eventEquals >= 12:
    #         self.torque = 0
    #     return str(round(self.torque, 2))
