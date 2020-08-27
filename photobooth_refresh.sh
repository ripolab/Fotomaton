#!/bin/bash

sleep 20
logger "sincronizamos git"
cd /home/pi/photobooth/photobooth_assets
git pull
