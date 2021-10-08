from os import system
import subprocess

modules = ['ant', 'gps', 'csv', 'messages', 'video', 'gpio', 'gear',
           'manager', 'accelerometer', 'hall_sensor', 'pyxbee_v2', 'weather']

broker_ip = '127.0.0.1'


for module in modules:
    system(f'cd {module} && python3 -m src.main {broker_ip} &')
    # system(f'python3 -m src.main &')

# system(f'cd new_bt && sudo bash start.sh &')
