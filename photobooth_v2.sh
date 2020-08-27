#!/bin/bash

sleep 20
logger "sincronizamos git"
cd /home/pi/photobooth/photobooth_assets
git pull

sleep 10
logger "iniciamos photobooth script"
cd /home/pi/photobooth
export DISPLAY=":0.0"
logger "iniciamos python photobooth"
python3 /home/pi/photobooth/photobooth_v2.py
