from serial import Serial
from time import sleep, time

s = Serial('/dev/ttyUSB1', 115200)
while True:
    s.write('ciao\n'.encode())
    print(s.readline())


