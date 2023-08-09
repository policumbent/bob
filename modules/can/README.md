# Bob CAN Module Documentation

The Bob CAN Module manages all the CAN communication happening between the
Raspberry Pi and the other ECUs on our bikes.

It uses [python-can](https://pypi.org/project/python-can/) and
[cantools](https://pypi.org/project/python-can/) as libraries to manage both the
CAN Bus and its messages.

## Preliminary operations

### Making ``can_logger.sh`` executable

Before doing anything, you have to make ``can_logger.sh`` executable, so you
will have to move in this folder and run:
```Bash
chmod +x can_logger.sh
```

### Dependencies installation

Since, at this point in time, this module does not have a virtual environment,
you will have to manually install its dependencies. You have to manually run:
```Bash
pip install requirements.txt
```

## ``python-can``

This library is used to manage the CAN Bus through SocketCAN. It defines a
``Bus`` object. It is needed both for sending messages and for receving them.
For the receiving part, it listens the bus and the object works in an
asynchronous way:

```Python
# Bus definition
bus = can.Bus(
        interface='socketcan',
        channel='can0',
        bitrate=500000,
        receive_own_messages=False
    )

...

# Asynchronous reading of the messages that are written on the bus
for msg in bus:
    # stuff
```

## ``cantools``

``cantools`` is used to perform actions on the messages: it provides functions
that are helpful in encoding and decoding CAN raw messages using a
[``.dbc`` file](https://www.csselectronics.com/pages/can-dbc-file-database-intro).
Our "original version" of the ``.dbc`` file is located in the
[poliCANbent repository](https://github.com/policumbent/poliCANbent/blob/main/dbc/policanbent.dbc),
but a copy of it is stored also in
[this repository](https://github.com/policumbent/bob/blob/main/modules/can/policanbent.dbc).
It may happen that the two versions of the file are not the same: the first to
be updated will and has to always be the one in the ``poliCANbent`` repository.

``cantools`` also provides a function which generates C libraries that encode
and decode messages.

## Structure and functions

The structure is very similar to other Bob modules, it behaves asynchronously
and it is linked to the MQTT server (as a publisher for the data that it reads
on the CAN Bus and as a subscriber for all other data that Bob provides).

### ``can_logger()``

The ``can_logger()`` function is called as a thread (using
[threading](https://docs.python.org/3/library/threading.html)), and it calles a
BASH script which runs
[``candump``](https://manpages.debian.org/testing/can-utils/candump.1.en.html),
so that a log of every message exchanged on the CAN Bus is created at every
system start-up and updated everytime that some ECUs writes on the Bus.

### ``mqtt()``

The ``mqtt()`` function is based on the same function present in the ``video``
module. It subscribes to some topics and whenever some module publishes on those
topics, it reads the data and send it on the CAN Bus.

_Notice:_ remember that, subscribing to the topics where this module publishes,
creates a loop of reading and writing of the same data.

### ``can_reader()``

This function is analogous to the previous one, but it does the opposite:
whenever a message is published on the CAN Bus, this module reads the message,
decodes it and publishes the decoded message in the correct topic. 