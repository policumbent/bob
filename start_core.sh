#!/usr/bin/env bash

sudo docker-compose up -d
cd modules/bt || exit 2
sudo bash start.sh
