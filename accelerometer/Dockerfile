FROM python:3.9
VOLUME /data
COPY src /src
RUN apt-get update
RUN apt-get install python3-smbus -y
RUN python3 -m pip install -r /src/requirements.txt
ENV ip 'mqtt-broker'
CMD python3 -m src.main ${ip}
