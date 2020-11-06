FROM python:3.7
COPY src /src
RUN READTHEDOCS=True python3 -m pip install -r /src/requirements.txt
CMD python3 -m src.test

