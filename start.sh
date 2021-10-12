#!/usr/bin/env bash

sudo docker-compose up -d
python3 start.py
cd new_bt || exit 2
sudo bash start.sh
