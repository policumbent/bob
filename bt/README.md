# Installation

1. `sudo apt install bluetooth libbluetooth-dev -y`
1. `sudo python3 -m pip install -r src/requirements.txt`
1. Change line `ExecStart=/usr/lib/bluetooth/bluetoothd` to `ExecStart=/usr/lib/bluetooth/bluetoothd --compat` in file `/etc/systemd/system/dbus-org.bluez.service`

