import json
import time
import serial
# from serial import Serial, serialutil
from .message import Message, MexType, MexPriority
from .alert import Alert, AlertPriority


class ArduinoSerial:
    ser = None
    started = False

    def __init__(self):
        print("Init serial class")
        # try:

        # APRIRE UNA COMUNICAZIONE SERIALE, USARE dmesg | grep tty* per capire cosa è connesso,
        # altrimenti cercare su internet
        ArduinoSerial.ser = serial.Serial('/dev/ttyS0', 9600)
        # wiringpi.wiringPiSetup()
        # ArduinoSerial.ser = wiringpi.serialOpen('/dev/ttyS0', 9600)
        ArduinoSerial.started = True
        print("\n\n\nOK: Serial opened")
        #
        # except serialutil.SerialException:
        #     print("\n\n\nErrore: SerialException")
        #     ArduinoSerial.started = False

    @staticmethod
    def send_gear_pos(p1, p2):
        if ArduinoSerial.started:
            x = {
                "pos_1": int(p1),
                "pos_2": int(p2)
            }

            json_s = json.dumps(x)
            # print("Serial: ", mex)
            # mex = '{"pos_2": 70, "pos_1": 142}'
            # print(mex)
            # print("Code: ", mex.encode())

            # ArduinoSerial.ser.writelines((mex.encode('ascii')))

            mex = json_s + "\n"
            ArduinoSerial.ser.write(str.encode(mex))
            # wiringpi.serialPuts(ArduinoSerial.ser, mex)
            print(mex)


PIN_UP = 27
PIN_DOWN = 17


class GpioMessage:
    down = -1
    reset = 0
    up = 1
