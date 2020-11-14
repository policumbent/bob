FROM python:3.9
COPY src /src
COPY start.sh /start.sh
COPY authorized_devices.conf /authorized_devices.conf
RUN apt update && apt install python3-pip python3-dev python3-setuptools bluetooth libbluetooth-dev -y
RUN pip3 install -r /src/requirements.txt
ENV ip 'mqtt-broker'
CMD /bin/bash start.sh

