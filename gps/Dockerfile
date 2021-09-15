FROM python:3.7
COPY src/requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt
COPY src /src
ENV ip 'mqtt-broker'
CMD python3 -m src.main ${ip}

