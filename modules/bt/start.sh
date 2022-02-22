#!/usr/bin/env bash

# enable bluetooth
service dbus start bluetoothd &
sleep 1
# run the program bluez
echo -e 'power on\ndiscoverable on\npairable on\nquit' | bluetoothctl

#sudo mount /dev/sda1 /mnt/usb

#cd /home/pi/Policumbent-ant-schermi/
./.venv/bin/python3 -m src.main
