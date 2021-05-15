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
python3 copy_common.py
sudo docker-compose build
sudo apt-get install bluetooth bluez libbluetooth-dev -y
sudo apt install python3-pip -y
sudo python3 -m pip install pybluez paho-mqtt

sudo cp dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service


uart1=$(eval "cat /boot/config.txt | grep enable_uart | wc -l")
if [[ $uart1 -eq 0 ]]
then
  echo 'enable_uart=1' | sudo tee -a  /boot/config.txt
fi

uart2=$(eval "cat /boot/config.txt | grep dtoverlay=uart2 | wc -l")
if [[ $uart2 -eq 0 ]]
then
  echo 'dtoverlay=uart2 # abilita la uart 2' | sudo tee -a  /boot/config.txt
fi

uart3=$(eval "cat /boot/config.txt | grep dtoverlay=uart3 | wc -l")
if [[ $uart3 -eq 0 ]]
then
  echo 'dtoverlay=uart3 # abilita la uart 3' | sudo tee -a  /boot/config.txt
fi


uart4=$(eval "cat /boot/config.txt | grep dtoverlay=uart4 | wc -l")
if [[ $uart4 -eq 0 ]]
then
  echo 'dtoverlay=uart4 # abilita la uart 4' | sudo tee -a  /boot/config.txt
fi


cond=$(eval "cat /boot/config.txt | grep dtoverlay=uart5 | wc -l")
if [[ $cond -eq 0 ]]
then
  echo 'dtoverlay=uart5 # abilita la uart 5' | sudo tee -a  /boot/config.txt
fi

cond=$(eval "cat /boot/config.txt | grep dtparam=i2c_arm=on | wc -l")
if [[ $cond -eq 0 ]]
then
  echo 'dtparam=i2c_arm=on # attiva i2c' | sudo tee -a  /boot/config.txt
fi

cond=$(eval "cat /boot/config.txt | grep dtparam=i2c_arm_baudrate=400000 | wc -l")
if [[ $cond -eq 0 ]]
then
  echo 'dtparam=i2c_arm_baudrate=400000 # i2c speed per accelerometro' | sudo tee -a  /boot/config.txt
fi

cond=$(eval "cat /boot/config.txt | grep gpu_mem=128 | wc -l")
if [[ $cond -eq 0 ]]
then
  echo 'gpu_mem=128' | sudo tee -a  /boot/config.txt
fi

cond=$(eval "cat /boot/config.txt | grep start_x=1 | wc -l")
if [[ $cond -eq 0 ]]
then
  echo 'start_x=1' | sudo tee -a  /boot/config.txt
fi


sudo chmod +x start.sh
sudo cp BOB.service /etc/systemd/system/
sudo systemctl enable BOB.service
sudo systemctl start BOB.service

# Installazione splash screen
echo "Installazione splash screen"
sudo apt install fbi -y
sudo cp splashscreen.service /etc/systemd/system/
sudo systemctl enable splashscreen.service
sudo systemctl start splashscreen.service
