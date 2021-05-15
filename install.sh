#!/bin/bash

echo "Installazione docker"

sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release -y
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y
sudo apt install docker-compose -y

echo "Installazione portainer"
# Installare portainer
sudo docker volume create portainer_data
sudo docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce

ip_command="ip addr show eth0 | grep \"inet\b\" | awk '{print $2}' | cut -d/ -f1"
ip=$(eval "$ip_command")
echo "Ricordati di impostare la password all'indirizzo http://"$ip":9000"

echo "Installazione BOB"
sudo apt install git -y
git clone https://github.com/policumbent/BOB.git
cd BOB
python3 copy_common.py
sudo docker-compose build
sudo apt-get install bluetooth bluez libbluetooth-dev -y
sudo apt install python3-pip -y
sudo python3 -m pip install pybluez

sudo cp dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service

sudo cp BOB.service /etc/systemd/system/
sudo systemctl enable BOB.service
sudo systemctl start BOB.service

# Installazione splash screen
echo "Installazione splash screen"
sudo apt install fbi -y
sudo cp splashscreen.service /etc/systemd/system/
sudo systemctl enable splashscreen.service
sudo systemctl start splashscreen.service
