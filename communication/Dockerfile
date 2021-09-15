FROM python:3.9
VOLUME /data
COPY src/requirements.txt /src/requirements.txt
RUN python3 -m pip install -r /src/requirements.txt
COPY src /src
ENV ip 'mqtt-broker'
CMD python3 -m src.main ${ip}


