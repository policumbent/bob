FROM python:3.9
COPY src /src
#RUN apt-get update && apt-get install apt-utils python3-dev python3-rpi.gpio -y

RUN python3 -m pip install -r /src/requirements.txt
CMD python3 -m src.main
