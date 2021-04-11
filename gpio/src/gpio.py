import json
import time
# import wiringpi  # pylint: disable=import-error
import RPi.GPIO as GPIO
import serial
# from serial import Serial, serialutil
from .message import Message, MexType, MexPriority
from .alert import Alert, AlertPriority


PIN_UP = 27
PIN_DOWN = 17


class GpioMessage:
    down = -1
    reset = 0
    up = 1


# todo: antibouncing
# todo: reset
class Gpio:
    def __init__(self, send_message, send_alert, send_pressed):
        self._send_message = send_message
        self._send_alert = send_alert
        self._send_pressed = send_pressed
        self._up = 0
        self._down = 0
        #
        # # NOTE: per gestire il reset e la registr. video
        # self._sensors = sensors
        # self._video = video
        # self._monitor = monitor
        # SERIAL
        # ArduinoSerial()

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
        self._send_pressed(GpioMessage.up)
        if self._down > 0:
            self.double_button_pressed()

    def down_pressed(self):
        self._down = time.time()
        print("Button down pressed")
        self._send_pressed(GpioMessage.down)
        if self._up > 0:
            self.double_button_pressed()

    def up_released(self):
        # self._gear.button_released()
        self._up = 0

    def down_released(self):
        # self._gear.button_released()
        self._down = 0

    def reset_pressed(self):
        self._send_pressed(GpioMessage.reset)
        # pass
        # il reset del csv da problemi
        # self._sensors.simulator.reset()
        # # self._monitor.csv_reset()
        # self._sensors.timer.reset()
        # self._sensors.speed.reset_distance()
        self._send_message(Message('RESET EFFETTUATO', MexPriority.medium, MexType.default, 5, 10))
        self._send_alert(Alert('Reset effettuato', AlertPriority.medium))

    def double_button_pressed(self):
        self.reset_pressed()
        time.sleep(0.2)

    def video_record(self):
        pass
        # if self._video is not None:
        #     self._video.video_record = not self._video.video_record
