import RPi.GPIO as GPIO
import time


class HallSensor:
    def __init__(self, pin):
        self.pin = pin
        self.timer = -1
        self.frequency = 0
        self.velocity = 0
        self.distance = 0
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

    def calc_freq(self):
        if self.period >= 0.0375:
            self.frequency = 1 / self.period

    def calc_vel(self):
        self.velocity = 1.5 * self.frequency* 3.6  # circumference * frequency

    def calc_space(self):
        self.distance = self.counter * 1.5

    def get_rpm(self):
        return self.frequency * 60

    def print_status(self):
        print(f" freq: {self.get_rpm(): .2f} giri/min vel: {self.velocity: .2f} km/h dist: {self.distance: .2f} m")

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