from os import listdir, system
from os.path import isdir, join
import time


# INSTALLO LE DIPENDENZE E LE LIBRERIE PER TUTTI I MODULI
print('Installare librerie e dipendenze? (y/N)')
resp = input()
if resp[0] == 'y':
    start = time.time()
    system('sudo apt update && sudo apt upgrade -y')
    directories = [f for f in listdir('modules') if isdir(join('modules', f))]
    for directory in directories:
        if directory[0] != '.':
            print(f'Installation requirements of {directory}')
            with open(f'./modules/{directory}/package_list.txt') as f:
                for line in f.readlines():
                    app = line.replace('\n', '')
                    system(f'sudo apt install {app} -y')
            system(f'cd ./modules/{directory}/ && poetry install')
    # system('sudo pip3 install paho-mqtt pybluez')
    system('sudo cp utility/ant-usb-sticks.rules /etc/udev/rules.d/')
    end = time.time()
    print(f'Installazione completata in {end - start} secondi')

print('Modificare bluez service?')
resp = input()
if resp[0] == 'y':
    system('sudo cp ./utility/dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service')

print('Modificare file config.txt?')
resp = input()
if resp[0] == 'y':
    system('sudo cp utility/config.txt /boot/config.txt')

print('Installare splashscreen?')
resp = input()
if resp[0] == 'y':
    system('sudo apt install fbi -y')
    system('sudo cp utility/splashscreen.service /etc/systemd/system/')
    system('sudo systemctl enable splashscreen.service')
    system('sudo systemctl start splashscreen.service')


print('Installare cockpit? (y/N)')
resp = input()
if resp[0] == 'y':
    system('sudo apt install cockpit')
    system('sudo apt install screenfetch')


