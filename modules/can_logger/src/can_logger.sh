#!/bin/bash

date_time=$(date +'%Y-%m-%d_%H-%M')
file_name=$date_time".log"

# send request to verify the status of every node on the bus, asking for a
# one-byte reply
cansend can0 000#R1

# write every messages sent on the bus in a log file
candump -tA can0 >> $file_name