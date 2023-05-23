import os

import asyncio
from asyncio import sleep

import can

from core import Mqtt, Database, log
from core.mqtt import Message

# External data collection: filters the incoming messages from the gearbox
# module and the GSM/GPS module and saves their data in the database 
async def data_read(data_reader):
    async for msg in data_reader:
        pass    # TODO: push GSM/GEAR data on database/CSVs