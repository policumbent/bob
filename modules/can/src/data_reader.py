import os

import asyncio
from asyncio import sleep

import can

from core import Mqtt, Database, log
from core.mqtt import Message


async def data_read(data_reader):
    async for msg in data_reader:
        pass    # TODO: push GSM/GEAR data on database/CSVs