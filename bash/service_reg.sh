#!/bin/bash

sudo cp /home/pi/sensor_receiver/bash/sensor_receiver_service /etc/init.d/sensor_receiver_service
sudo chmod 755 /etc/init.d/sensor_receiver_service
sudo update-rc.d sensor_receiver_service defaults