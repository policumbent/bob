FROM python:3.9
VOLUME /data
RUN  apt-get update && apt-get install libusb-dev apt-utils -y
COPY src/requirements.txt /src/requirements.txt
RUN python3 -m pip install -r /src/requirements.txt
COPY src /src
ENV ip 'mqtt-broker'
CMD python3 -m src.main ${ip}
