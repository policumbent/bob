# TODO: Refactor this class 



import time

from collections import deque

from .device import AntDevice, DeviceTypeID
from .ant.easy.channel import Channel

# from core.message import Message, MexType, MexPriority

# CHANNEL_PERIOD_VAL = 32768/MESSAGE_RATE(HZ)
# MESSAGE_RATE = 32768/32768 = 32768/8182 = 4HZ
# TEMPO_PER_LA_MEDIA = 3s
# LUNGHEZZA_VETTORE_MEDIA = TEMPO_PER_LA_MEDIA * MESSAGE_RATE = 4 * 3
# POTENZA MEDIA: 1s -> 4 || 3s -> 12 || 5s -> 20 || 10s --> 40 (impostare il valore desiderato)
from .settings import Settings


class Powermeter(AntDevice):
    def __init__(self, node, sensor_id=0, device_type=DeviceTypeID.powermeter):
        super().__init__(node, sensor_id)

        self._device_type_id = device_type.value

        # lunghezza_vettore_media = settings.average_power_time * 4
        # lunghezza_vettore_media_1s = 4

        self._power: int = 0
        self._calibration_value = 0
        self._calibration = False
        self._state = False
        # self._settings = settings

        self.count = 0
        self.count2 = 0
        self._cadence = 0
        self.eventEquals = 0
        self.n_average = 10
        self.timeStampP = 0
        self.eventCountP = 0
        self.torqueTicksStampP = 0

        # self.offset = 500  # 495
        self.calibration_count = 0
        # self.send_message = send_message
        self.lastRxTime = time.time()
        self.newData = False
        self.data = None
        self.torque = 0  # type: float
        self.averagePower = 0
        self.averagePower1s: int = 0
        self.count3 = 1
        self.lastAverageTime = 0
        self.lastAverageTime1s = 0
        # self.average_array = deque(lunghezza_vettore_media * [0])
        # self.average_array_1s = deque(lunghezza_vettore_media_1s * [0])
        self._last_rx = time.time()

        # self._calibration_lock = threading.Lock()
        # self._worker_thread = Thread(target=self._run, daemon=True)
        # self._worker_thread.start()

        # inizializzazione del channel ant
        self._init_channel()

    # NOTE: specializzazione metodi astratti di `AntReader`

    def _init_channel(self):
        if self._channel is None:
            self._channel = self._create_channel()

        # callbacks for data
        self._channel.on_broadcast_data = self._receive_new_data
        self._channel.on_burst_data = self._receive_new_data

        # PROVARE VARI PERIODI E VEDERE COSA SUCCEDE --> INZIALe 8085
        self._channel.set_period(8182)
        self._channel.set_search_timeout(255)
        self._channel.set_rf_freq(57)

        # 11 -> DEVICE ID DEL MISURATORE || 30636 -> id misuratore taurus
        # powermeter_id = self._settings.power_sensor_id
        self._channel.set_id(self._sensor_id, self._device_type_id, 0)

        # open channel
        self._channel.open()

    def _receive_new_data(self, data):
        # t1 = time.time()
        self.data = data
        self.newData = True
        self.count += 1
        self._last_rx = time.time()
        # t2 = time.time()
        # print("Tempo acquisizione: " + str(t2 - t1))

    def read_data() -> dict:
        pass

    # NOTE: metodi propri della classe

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

    # def signal(self, value: str):
    #     if value == 'calibrate_powermeter':
    #         self.calibration = True

    # def export(self):
    #     return {
    #         'average_power': self.getAverage(),
    #         # 'power': self.value,
    #         '1s_power': self.get_average_1s(),
    #         'cadence': self.cadence
    #     }

    # def update_settings(self, settings: Settings):
    #     # todo: settings e gestire la calibrazione
    #     pass

    @property
    def value(self):
        if (time.time() - self._last_rx) > 5:
            self._power = 0
        return round(self._power)

    @property
    def cadence(self):
        if (time.time() - self._last_rx) > 5:
            self._cadence = 0
        return self._cadence

    @property
    def state(self):
        return self._state

    @property
    def calibration(self):
        with self._calibration_lock:
            return self._calibration

    @calibration.setter
    def calibration(self, value: bool):
        with self._calibration_lock:
            self._calibration = value

    # TODO: DEPRECATE
    def set_channel(self, channel_powermeter: Channel):
        # CANALE POTENZA
        channel_powermeter.on_broadcast_data = self.on_data_power
        channel_powermeter.on_burst_data = self.on_data_power
        # PROVARE VARI PERIODI E VEDERE COSA SUCCEDE --> INZIALe 8085
        channel_powermeter.set_period(8182)
        channel_powermeter.set_search_timeout(255)
        channel_powermeter.set_rf_freq(57)
        # 11 -> DEVICE ID DEL MISURATORE || 30636 -> id misuratore taurus
        powermeter_id = self._settings.power_sensor_id
        channel_powermeter.set_id(powermeter_id, 11, 0)

    # TODO: DEPRECATE
    def on_data_power(self, data):
        # t1 = time.time()
        self.data = data
        self.newData = True
        self.count += 1
        self._last_rx = time.time()
        # t2 = time.time()
        # print("Tempo acquisizione: " + str(t2 - t1))

    #  print(str(self.newData))

    # 0 -> 0x20 potenza / 0x10 calibrazione
    # 1 -> Update Event Count -> Rotation event counter increments with each completed pedal revolution.
    # Range: 256
    # 2 -> Slope MSB -> Slope defines the variation of the output frequency.
    # 3 -> Slope LSB -> Units: 1/10Nm/Hz  Range: 100 - 500
    # 4 -> Time Stamp MSB -> Time of most recent rotation event
    # 5 -> Time Stamp LSB -> Units: 1/2000s  Range: 32.7s
    # 6 -> Torque Ticks Stamp MSB -> Count of most recent torque event
    # 7 -> Torque Ticks Stamp LSB -> Range: 65536 ticks

    def calculate_average_power(self):
        if (time.time() - self.lastAverageTime) < 0.25:
            return
        self.average_array.appendleft(self.value)
        self.average_array.pop()
        somma = 0
        for elem in self.average_array:
            somma += elem
        self.lastAverageTime = time.time()
        self.averagePower = somma / len(self.average_array)

    def calculateAveragePower1s(self):
        if (time.time() - self.lastAverageTime1s) < 0.25:
            return
        self.average_array_1s.appendleft(self.value)
        self.average_array_1s.pop()
        somma = 0
        for elem in self.average_array_1s:
            somma += elem
        self.lastAverageTime1s = time.time()
        self.averagePower1s = somma / len(self.average_array_1s)

    def calculatePower(self, data):
        if data[0] == 1:
            # print ("Offset attuale: "+ str(offset)+" Offset salvato: "+ str(self.offset))
            # todo: da testare il meccanismo di calibrazione
            if self.calibration_count > 0:
                self._calibration_value = (data[6] << 8) + data[7]
                # todo: se io mostro un messaggio per un secondo e i pacchetti arrivano con una frequenza maggiore
                # non avrò dati aggiornati a schermo per la calibrazione, bisogna inventarsi qualcosa
                # self.mex.set("Calibrazione tra " +
                #              str(self.calibrazione) + "pacchetti", 3, 1)
                # self.send_message(Message("NON TOCCARE - " + str(self._calibration_value),
                #                           MexPriority.medium, MexType.default, 1, 1))
                self.calibration_count -= 1
                return

            if self.calibration_count == 0:
                # todo: verificare che lo shift riporti un risultato giusto pure qui
                self._calibration_value = (data[6] << 8) + data[7]
                # print("CALIBRAZIONE ", self._calibration_value)
                # self.send_message(Message("Calibrato a " + str(self._calibration_value),
                #                           MexPriority.medium, MexType.default, 5, 10))
                #                state.update("calibration_value": offset)
                #                 Settings.save()
                #                 Settings.settings_request = True
                self.calibration_count -= 1
                return

        if data[0] == 32:
            event_count = data[1]
            slope = (data[2] << 8) + data[3]
            timeStamp = (data[4] << 8) + data[5]
            torqueTicksStamp = (data[6] << 8) + data[7]

            if event_count == self.eventCountP:
                self.eventEquals += 1
                return
            else:
                self.eventEquals = 0
            # if (data[0] != 32):
            #     return
            # ## CALCOLO CADENZA
            # # periodoCadenza = (timeStamp - timeStampP) x 0.0005 / (event_count - eventCountP)
            # # cadenza = round(60/periodoCadenza)
            # print (str(event_count) + " " + str(self.eventCountP))
            eventCountC = event_count - self.eventCountP
            if eventCountC < 0:
                eventCountC = event_count - self.eventCountP + 256

            deltaTime = timeStamp - self.timeStampP
            if deltaTime < 0:
                deltaTime += 65535
            if deltaTime == 0:
                deltaTime = 0.000001

            cadencePeriod = deltaTime * 0.0005 / eventCountC
            if cadencePeriod != 0:
                cadence = 60 / cadencePeriod
                self.cadence = round(cadence)
            else:
                cadence = 1
            # ## CALCOLO POTENZA
            # print (data[0])
            elapsedTime = deltaTime * 0.0005
            torqueTicks = torqueTicksStamp - self.torqueTicksStampP
            if torqueTicks == 0:
                torqueTicks = 0.0000001
            if torqueTicks < 0:
                torqueTicks += 65536

            torqueFrequency = (
                1 / (elapsedTime / torqueTicks)
            ) - self._calibration_value
            #    torqueFrequency = 1
            #    print ("Slope: " + str(slope))
            torque = torqueFrequency / (slope / 10.0)
            #    print ("torque: " + str(torque))
            power = torque * cadence * 3.1415 / 30
            # print ("deltaTime: " + str(deltaTime))
            # print ("TorqueTicks: " + str(torqueTicks))
            # print ("elapsedTime: " + str(elapsedTime))
            # print ("torqueFrequency: " + str(torqueFrequency))
            # print ("power: " + str(power))
            # power =(100*torque * float(self.cadence) * 3.1415 / 30.0)
            if self.count3 >= 0:
                power = 0
                self.count3 -= 1
            self._power = power
            self.torque = torque
            self.timeStampP = timeStamp
            self.eventCountP = event_count
            self.torqueTicksStampP = torqueTicksStamp
            self.lastRxTime = time.time()

    def getCadence(self):
        if (time.time() - self.lastRxTime) > 4:
            self.cadence = 0
        if self.eventEquals >= 12:
            self.cadence = 0
        return self.cadence

    def get(self) -> int:
        if self.eventEquals >= 12:
            self._power = 0
        return round(self._power)

    def get_count(self):
        return self.count2

    def getAverage(self) -> int:
        if self.averagePower is None:
            return 0
        return round(self.averagePower)

    def get_average_1s_str(self) -> int:
        if self.averagePower1s is None:
            return 0
        return round(self.averagePower1s)

    def get_average_1s(self) -> int:
        if self.averagePower1s is None:
            return 0
        return round(self.averagePower1s)

    def getCountString(self):
        return str(self.get_count())

    def getTorque(self):
        if (time.time() - self.lastRxTime) > 4:
            self.torque = 0
        if self.eventEquals >= 12:
            self.torque = 0
        return str(round(self.torque, 2))
