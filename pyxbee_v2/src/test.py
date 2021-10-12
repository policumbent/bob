from serial import Serial
from time import sleep, time

s = Serial('/dev/ttyUSB0', 115200)
while True:
    t_i = time()
    print(s.readline().decode())
    print(time()-t_i)

