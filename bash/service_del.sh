#!/bin/bash

sudo update-rc.d -f sensor_receiver_service remove
sudo rm /etc/init.d/sensor_receiver_service