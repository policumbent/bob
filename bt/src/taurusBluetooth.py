import threading
from typing import List, Tuple

import bluetooth
import json

from .settings import Settings
from .message import Message, MexType, MexPriority
from .alert import Alert, AlertPriority

port = 1
backlog = 3
BUFF = 1024
uuid = "eb60ae08-b17e-11e9-a2a3-2a2ae2dbcce4"


def is_authorized_device(address: tuple):
    with open("authorized_devices.conf", 'r') as f:
        values = f.readlines()
    address = address[0].lower()
    for value in values:
        value = value.lower()
        value = value.replace('\n', '')
        # print(address, '==', value)
        if value == address:
            return True
    print("Device non autorizzato")
    return False


# todo: gestire lock
class TaurusBluetooth:

    # def get_update(self) -> Settings:
    #     with self._settings_lock:
    #         return self._settings

    # def has_new_update(self) -> bool:
    #     with self._settings_lock:
    #         return self._new_update

    def update_settings(self, settings: dict):
        # with self._settings_lock:
        self._settings = settings

    def __init__(self, settings: dict, send_settings, send_signal, send_message, send_alert):
        self._settings = settings
        self._new_settings = settings
        self._send_settings = send_settings
        self._send_signal = send_signal
        self._send_message = send_message
        self._send_alert = send_alert
        # self._settings_lock = threading.Lock()
        # self._signals_lock = threading.Lock()
        self._new_update = False

        self._server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._server_sock.bind(("", 1))
        print("Listen")
        self._server_sock.listen(backlog)
        bluetooth.advertise_service(self._server_sock, "Taurus", uuid)
        print("Advertise service")

    def handle(self):
        client_sock, address = self._server_sock.accept()
        self.handle_client(client_sock, address)

    def handle_client(self, client_sock: bluetooth.BluetoothSocket, address):
        print("Received data from ", address)
        if is_authorized_device(address):
            data = client_sock.recv(BUFF)
            reply, new_settings = self.handle_mex(data)
            if self._new_update:
                self._new_update = False
                self._send_settings(new_settings)
            client_sock.send(reply.encode("utf-8"))
        client_sock.close()

    def handle_mex(self, data_o: bytes):
        # todo: gestire il caso di errore
        data = data_o.decode()
        data = data.lower()
        v = data.split(';')
        case = v[0]
        if v.__len__() > 1:
            value = v[1]
        else:
            value = False

        # print(data)
        # CALIBRAZIONE CAMBIO
        if case == "gear":
            # reply, new_settings = self.han
            return self.handle_gear(data_o)
            # return "NOT_IMPLEMENTED_YET"

        # SETTINGS
        if self._settings.__contains__(case):
            t = self._settings[case]
            if isinstance(t, bool):
                reply, new_settings = self.bool_value_change(case, value)
                return reply, new_settings
            if isinstance(t, int):
                reply, new_settings = self.int_value_change(case, value)
                return reply, new_settings
            self._send_message(
                Message('{} impostato a '.format(case.capitalize()), MexPriority.medium, MexType.default, 5, 15)
            )
            self._send_alert(
                Alert('{} impostato a '.format(case.capitalize()), AlertPriority.medium)
            )

        # SEGNALI
        elif case == "reset":
            return self.reset(), None
        elif case == "powermeter_calibration":
            return self.powermeter_calibration(), None
        # elif case == "upload_csv":
        #     return self._monitor.upload_csv()

        # STATI
        # elif case == "p13":
        #     return self.p13_set(value)
        # elif case == "video_record":
        #     return self.video_record(value)

        elif case == "update":
            return self.update_request(), self._settings.copy()
        return "ERROR"

    def bool_value_change(self, name, value):
        # todo: aggiungere un try,  e gestire l'errore
        # with self._settings_lock:
        value = value == 'true'
        new_settings = self._settings.copy()
        new_settings[name] = value
        self._new_update = True
        # print(json.dumps(self._settings, indent=4))
        # save_settings(self._settings)
        # mex = name + " impostato a " + str(value)
        # self._mex.set(mex, MexPriority.medium, 5)
        return "OK", new_settings

    def int_value_change(self, name, value):
        # todo: aggiungere un try, e gestire l'errore
        # with self._settings_lock:
        new_settings = self._settings.copy()
        new_settings[name] = int(value)
        # self._settings[name] = int(value)
        self._new_update = True
        return "OK", new_settings

    def reset(self):
        print("Reset")
        self._send_signal('reset')
        self._send_message(Message('Reset effettuato', MexPriority.medium, MexType.default, 5, 15))
        self._send_alert(Alert('Reset effettuato', AlertPriority.low))
        return "OK"

    def powermeter_calibration(self):
        print("Powermeter calibration")
        self._send_signal('powermeter_calibration')
        self._send_alert(Alert('Calibrazione power meter richiesta', AlertPriority.low))
        return "OK"

    # def p13_set(self, value):
    #     value = value == 'true'
    #     # if self.__video is not None:
    #     #     self.__video.p13 = value
    #     return "OK"

    # def video_record(self, value):
    #     value = value == 'true'
    #     # if self.__video is not None:
    #     #     self.__video.video_record = value
    #     return "OK"

    def update_request(self):
        update = self._settings.copy()
        return json.dumps(update)

    def handle_gear(self, mex: bytes):
        print("Gear calibration")
        # with self._settings_lock:
        value, new_setting = self.gear_mex_handler(mex)
        self._new_update = True
        # self.__sensors.powermeter.calibration = True
        return value, new_setting

    def gear_mex_handler(self, data: bytes) -> Tuple[str, dict]:
        data = data.decode()
        v = data.split(';')
        v = v[1:47]
        # print(v[0])
        if v[0] == "GET":
            return self.gear_encode_mex()
        if v[0] == "SET":
            return self.gear_decode_mex(v)
            # todo: implementare la cambiata da app
            # return mex, new_setting
            # todo: creare signal 'refresh_position' con questo contenuto
            # servo1_pos, servo2_pos = self.get_angle(self.gear, Mode.UP)
            # print("Aggiornamento posizione servo", self.gear)
            # self.servo_move(servo1_pos, servo2_pos)
            # self.save_gear_positions()
            # self.mex.set("Calibrazione cambio effettuata")
            # return response
        if v[0] == "SHIFT":
            pass
            # return self.shift(v)

    def gear_decode_mex(self, data):
        # print(len(data))
        if len(data) >= 45:
            v = dict()
            v['up_positions_s1'] = data[1:12]
            v['up_positions_s2'] = data[12:23]
            v['down_positions_s1'] = data[23:34]
            v['down_positions_s2'] = data[34:45]
            new_settings = self._settings.copy()
            new_settings['gear'] = v
            return "OK", new_settings
        return "ERROR", self._settings.copy()

    def gear_encode_mex(self):
        d = "VALUES;"
        new_settings = self._settings.copy()
        d += ';'.join(str(e) for e in new_settings['gear']['up_positions_s1']) + ';'
        d += ';'.join(str(e) for e in new_settings['gear']['up_positions_s2']) + ';'
        d += ';'.join(str(e) for e in new_settings['gear']['down_positions_s1']) + ';'
        d += ';'.join(str(e) for e in new_settings['gear']['down_positions_s2'])
        # print(d)
        return d, new_settings
