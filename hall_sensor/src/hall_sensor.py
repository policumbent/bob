import RPi.GPIO as GPIO
import time


class HallSensor:
    def __init__(self, pin):
        self.pin = pin
        self.timer = -1
        self.frequency = 0
        self.counter = 0

    def start_timer(self):
        self.start = time.time()

    def end_timer(self):
        self.stop = time.time()
        self.period = self.stop - self.start

    def clock(self, channel):
        self.counter += 1
        if self.timer == -1:
            self.timer = time.time()
        else:
            tme = time.time()
            self.period = tme - self.timer
            self.timer = tme
            self.calc_freq()
            self.calc_vel()
            self.calc_space()
            self.print_status()  # per il debugging

    def calc_freq(self, period):
        if period >= 0.036:
            self.frequency = 1 / period

    @property
    def speed(self):
        # todo: mettere a 0 quando un passaggio da più di 4s
        return round(self.__settings.circumference * self.frequency * 3.6 / 1000, 2)  # circumference * frequency

    @property
    def distance(self):
        return round(self.counter * self.__settings.circumference / pow(10, 6), 2)

    def get_rpm(self):
        return self.frequency * 60

    def print_status(self):
        print(f" freq: {self.get_rpm(): .2f} giri/min vel: {self.speed: .2f} km/h dist: {self.distance: .2f} m")

    def print_pin_status(self):
        print(GPIO.input(self.pin))  # prints the status of the pin: HIGH(1)/LOW(0)


def main():
    hall_sensor = HallSensor(24)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(hall_sensor.pin, GPIO.IN)

    GPIO.add_event_detect(hall_sensor.pin, GPIO.FALLING, callback=hall_sensor.clock)  # passing from HIGH to LOW

    while True:
        time.sleep(1)

    GPIO.cleanup()


main()