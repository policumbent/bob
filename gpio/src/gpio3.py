import json
import time
# import wiringpi  # pylint: disable=import-error
import RPi.GPIO as GPIO
import serial
# from serial import Serial, serialutil


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


# todo: antibouncing
class Gpio:
    def __init__(self, mex, gear):
        self._gear = gear
        self._up = 0
        self._down = 0
        #
        # # NOTE: per gestire il reset e la registr. video
        # self._sensors = sensors
        # self._video = video
        # self._monitor = monitor
        # SERIAL
        ArduinoSerial()

        GPIO.setwarnings(False)  # Ignore warning for now
        # GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        # todo: cosa significa GPIO.BCM

        GPIO.setmode(GPIO.BCM)  # Use gpio pin numbering

        GPIO.setup(PIN_UP, GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)
        # Set pin 10 to be an input pin and set initial value to be pulled low (off)

        GPIO.setup(PIN_DOWN, GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)
        # Set pin 10 to be an input pin and set initial value to be pulled low (off)

        GPIO.add_event_detect(PIN_UP, GPIO.BOTH, callback=self.up)
        GPIO.add_event_detect(PIN_DOWN, GPIO.RISING, callback=self.down)

        self.mex = mex
        #
        # self._worker = threading.Thread(target=self.loop, daemon=False)
        # self._worker.start()

    def up(self, channel):
        if not GPIO.input(PIN_UP):
            self.up_pressed()
        else:
            self.up_released()

    def down(self, channel):
        if not GPIO.input(PIN_DOWN):
            self.down_pressed()
        else:
            self.down_released()

    def up_pressed(self):
        self._up = time.time()
        print("Button up pressed")
        self._gear.gear_up()
        if self._down > 0:
            self.double_button_pressed()

    def down_pressed(self):
        self._down = time.time()
        print("Button down pressed")
        self._gear.gear_down()
        if self._up > 0:
            self.double_button_pressed()

    def up_released(self):
        self._gear.button_released()
        self._up = 0

    def down_released(self):
        self._gear.button_released()
        self._down = 0

    def reset_pressed(self):
        # pass
        # il reset del csv da problemi
        # self._sensors.simulator.reset()
        # # self._monitor.csv_reset()
        # self._sensors.timer.reset()
        # self._sensors.speed.reset_distance()
        self.mex.set("RESET EFFETTUATO", 4, 2, 5)
        Notice.new("Reset effettuato")

    def double_button_pressed(self):
        self.reset_pressed()
        time.sleep(0.2)

    def video_record(self):
        pass
        # if self._video is not None:
        #     self._video.video_record = not self._video.video_record
