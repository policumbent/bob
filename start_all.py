from os import system

modules = ['ant', 'video', 'messages', 'gps', 'LED', 'accelerometer', 'phoenix', 'gear', 'power_speed_target',
           'manager', 'pyxbee_v2', 'pyxbee_v3', 'csv', 'bt', 'hall_sensor', 'weather', 'communication', 'gpio',
           'external_mqtt']


broker_ip = '127.0.0.1'


for module in modules:
    system(f'cd modules/{module} && python3 -m src.main {broker_ip} &')