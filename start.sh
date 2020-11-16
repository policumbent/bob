#!/usr/bin/env bash

sudo docker-compose up -d
cd bt || exit 2
sudo bash start.sh &
