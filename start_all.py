from os import system

modules = ['ant', 'gps', 'csv', 'messages', 'video', 'gpio', 'gear',
           'manager', 'accelerometer', 'hall_sensor', 'pyxbee_v2', 'weather']

broker_ip = '127.0.0.1'


for module in modules:
    system(f'cd modules/{module} && python3 -m src.main {broker_ip} &')