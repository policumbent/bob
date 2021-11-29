from os import system

modules = ['ant', 'video', 'messages', 'gps', 'LED', 'accelerometer', 'phoenix', 'gear', 'power_speed_target', 'manager', 'pyxbee_v2', 'pyxbee_v3', 'csv', 'bt', 'hall_sensor', 'weather', 'communication', 'gpio', 'gear_old', 'external_mqtt']
broker_ip = '127.0.0.1'
print("Avaliable modules: ", modules)
module_name = input('Module name: ')

if module_name in modules:
    system(f'cd modules/{module_name} && python3 -m src.main {broker_ip}')
