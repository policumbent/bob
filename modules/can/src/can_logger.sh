#!/bin/bash

curr_date = $(date +"%Y-%m-%dT%H:%M:%S%z")
candump -tz can0 >> $curr_date