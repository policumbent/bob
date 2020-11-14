FROM python:3.7
COPY src /src
COPY resources /resources
RUN apt-get update && apt-get install libopenjp2-7 libtiff5 -y
RUN READTHEDOCS=True python3 -m pip install -r /src/requirements.txt
CMD python3 -m src.main

