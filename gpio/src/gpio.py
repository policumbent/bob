import time
import RPi.GPIO as GPIO
from .common_files.message import Message, MexType, MexPriority
from .common_files.alert import Alert, AlertPriority


PIN_UP = 17
PIN_DOWN = 27


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
        self.__up = {
            'pressed': False,
            'last': .0
        }
        self.__down = {
            'pressed': False,
            'last': .0
        }
        self.__pressure_time = .4  # secondi
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
        GPIO.add_event_detect(PIN_DOWN, GPIO.BOTH, callback=self.down)
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
        self.__up['pressed'] = True
        t = time.time()
        if (t - self.__up['last']) > self.__pressure_time:
            print("Button up pressed")
            self.__up['last'] = t
            self._send_pressed(GpioMessage.up)
            self.double_button_pressed()

    def down_pressed(self):
        self.__down['pressed'] = True
        t = time.time()
        if (t - self.__down['last']) > self.__pressure_time:
            print("Button down pressed")
            self.__down['last'] = t
            self._send_pressed(GpioMessage.down)
            self.double_button_pressed()

    def up_released(self):
        self.__up['pressed'] = False
        self.__up['last'] = time.time()

    def down_released(self):
        self.__down['pressed'] = False
        self.__down['last'] = time.time()

    def reset_pressed(self):
        self._send_pressed(GpioMessage.reset)
        self._send_message(Message('RESET EFFETTUATO', MexPriority.medium, MexType.default, 5, 10))
        self._send_alert(Alert('Reset effettuato', AlertPriority.medium))

    def double_button_pressed(self):
        if self.__down['pressed'] and self.__up['pressed']:
            self.reset_pressed()
            print('Double pressed')

    def video_record(self):
        pass
        # if self._video is not None:
        #     self._video.video_record = not self._video.video_record
