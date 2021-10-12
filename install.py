from os import listdir, system
from os.path import isdir


# INSTALLO LE DIPENDENZE E LE LIBRERIE PER TUTTI I MODULI
print('Installare librerie e dipendenze? (y/N)')
resp = input()
if resp[0] == 'y':
    system('sudo apt update && sudo apt upgrade -y')
    directories = [f for f in listdir() if isdir(f)]
    for directory in directories:
        if directory != 'common_files' and directory[0] != '.' and \
                directory != 'utility' and directory != 'example_module':
            print(f'Installation requirements of {directory}')
            system(f'python3 -m pip install -r ./{directory}/src/requirements.txt')
            with open(f'./{directory}/package_list.txt') as f:
                for line in f.readlines():
                    app = line.replace('\n', '')
                    system(f'sudo apt install {app} -y')
    system('python3 copy_common.py')

    system('sudo cp utility/ant-usb-sticks.rules /etc/udev/rules.d/')
    system('sudo pip3 install paho-mqtt pybluez')

print('Modificare bluez service?')
resp = input()
if resp[0] == 'y':
    system('sudo cp utility/dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service')

print('Modificare file config.txt?')
resp = input()
if resp[0] == 'y':
    system('sudo cp utility/config.txt /boot/config.txt')

print('Installare servizio per auto avvio?')
resp = input()
if resp[0] == 'y':
    system('sudo chmod +x start.sh')
    system('sudo cp utility/BOB.service /etc/systemd/system/')
    system('sudo systemctl enable BOB.service')
    system('sudo systemctl start BOB.service')


print('Installare splashscreen?')
resp = input()
if resp[0] == 'y':
    system('sudo apt install fbi -y')
    system('sudo cp utility/splashscreen.service /etc/systemd/system/')
    system('sudo systemctl enable splashscreen.service')
    system('sudo systemctl start splashscreen.service')


