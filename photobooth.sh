#!/bin/bash

logger "iniciamos photobooth script"
cd /home/pi/photobooth
export DISPLAY=":0.0"
logger "iniciamos python photobooth"
python3 /home/pi/photobooth/photobooth.py
