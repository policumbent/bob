FROM python:3.9-alpine
COPY src /src
RUN python3 -m pip install -r /src/requirements.txt
ENV ip 'mqtt-broker'
CMD python3 -m src.main ${ip}


