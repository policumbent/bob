#!/bin/bash

date_time=$(date +'%Y-%m-%d_%H-%M')
file_name=$date_time".log"

candump -tA can0 >> $file_name