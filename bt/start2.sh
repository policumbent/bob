#!/usr/bin/env bash

# enable bluetooth
sudo systemctl start bluetooth

sleep 1
# run the program bluez
sudo echo -e 'power on\ndiscoverable on\npairable on\nquit' | bluetoothctl

#sudo mount /dev/sda1 /mnt/usb

#cd /home/pi/Policumbent-ant-schermi/
python3 -m src.main
