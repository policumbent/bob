import threading
import time
import json

from enum import IntEnum
from .common_files.message import Message
from .common_files.sensor import Sensor
from .settings import Settings
from .arduino_serial import ArduinoSerial
from pathlib import Path

LAST_GEAR_FILE_PATH = "gear_last_pos.json"
POS_FILE_PATH = "gear_pos.config"


class Gear(Sensor):

    def signal(self, value: str):
        pass

    def export(self) -> dict:
        return {
            'gear': self.value
        }

    def __init__(self, send_message, settings: Settings):
        self._send_message = send_message
        self.gear_changed = False
        self.count = 0
        self._settings_lock = threading.Lock()
        self._settings: Settings = settings
        self.gear = self.read_last_gear()
        # # VETTORE CON GLI ANGOLI DEI SERVO PER OGNI MARCIA
        # self.read_gear_positions()

    @property
    def value(self):
        return self.gear

    def get(self):
        return str(self.gear)

    def get_count(self):
        return self.count

    def gear_up(self):
        if self.gear < 11 and not self.gear_changed:
            new_gear = self.gear + 1
            servo1_pos, servo2_pos = self.get_angle(new_gear, Mode.UP)
            print("Movimentazione servo in salita: ", new_gear)
            self.servo_move(servo1_pos, servo2_pos)
            self.gear = new_gear
            self.save_last_gear()
            self.gear_changed = True
            time.sleep(0.2)

    def gear_down(self):
        if self.gear > 1 and not self.gear_changed:
            new_gear = self.gear - 1
            servo1_pos, servo2_pos = self.get_angle(new_gear, Mode.DOWN)
            print("Movimentazione in discesa", new_gear)
            self.servo_move(servo1_pos, servo2_pos)
            self.gear = new_gear
            self.save_last_gear()
            self.gear_changed = True
            time.sleep(0.1)

    def button_released(self):
        self.gear_changed = False

    def save_last_gear(self):
        print("Salvataggio ultima marcia")
        data = {
            "last_gear": int(self.value)
        }
        try:
            with open(LAST_GEAR_FILE_PATH, "w") as write_file:
                json.dump(data, write_file)
            print("Ultima marcia salvata")
        except Exception as e:
            print(e)
            print("Errore salvataggio ultima marcia inserita")

    def read_last_gear(self):
        # FUNZIONE PER RECUPERARE DA UN FILE DI TESTO L'ULTIMA MARCIA INSERITA
        print("Lettura ultima marcia")
        last_position = 1
        pos_gear_file = Path(LAST_GEAR_FILE_PATH)
        if not pos_gear_file.is_file():
            print("ERRORE: Non è possibile recuperare l'ultima posizione")
            self.gear = 1
            self.save_last_gear()
            return last_position
        try:
            print("Caricamento impostazioni")
            with open(LAST_GEAR_FILE_PATH, "r") as read_file:
                data = json.load(read_file)
            print(data)
            last_position = data["last_gear"]
            return last_position
        except Exception as e:
            print(e)
            print("C'è stato un errore nella lettura marcia")
            return 1

    def save_gear_positions(self):
        print("Salvataggio posizioni marce")
        with open(POS_FILE_PATH, "w") as write_file:
            write_file.write(self.encode_mex())
            print("Posizioni servomotori cambio salvata")

    def get_angle(self, gear, up_or_down):
        if gear > 11:
            print("Errore posizione")
            gear = 11
        if gear < 1:
            print("Errore posizione")
            gear = 1

        if up_or_down == Mode.UP:
            pos_p1 = self._settings.gear_settings['up_positions_s1'][gear - 1]
            pos_p2 = self._settings.gear_settings['up_positions_s2'][gear - 1]
        else:
            pos_p1 = self._settings.gear_settings['down_positions_s1'][gear - 1]
            pos_p2 = self._settings.gear_settings['down_positions_s2'][gear - 1]
        return pos_p1, pos_p2

    def servo_move(self, servo1_pos, servo2_pos):
        self.count += 1
        print("Movimentazione servo")
        print("\tservo 1 -> ", servo1_pos)
        print("\tservo 2 -> ", servo2_pos)
        ArduinoSerial.send_gear_pos(servo2_pos, servo1_pos)

    def shift(self, mode: int):
        if mode == Mode.UP:
            self.gear_up()
        else:
            self.gear_down()

    # metodo usato dall'app
    # def shift(self, v):
    #     new_gear = int(v[1])
    #     if 11 >= new_gear >= 1:
    #         servo1_pos, servo2_pos = self.get_angle(new_gear, Mode.UP)
    #         print("Movimentazione servo in salita: ", new_gear)
    #         self.servo_move(servo1_pos, servo2_pos)
    #         self.gear = new_gear
    #         self.save_last_gear()
    #         time.sleep(0.2)
    #         return "OK " + str(self.gear)
    #     return "ERRORE cambiata"

    @classmethod
    def map(cls, value, in_min, in_max, out_min, out_max):
        return (value-in_min) * (out_max-out_min) / (in_max-in_min) + out_min

    def read_input(self):
        v1 = input("Servo 1")
        v2 = input("Servo 2")
        self.servo_move(v1, v2)


class Mode:
    UP = 1
    DOWN = -1
