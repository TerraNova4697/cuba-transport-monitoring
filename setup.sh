#!/bin/bash

sudo pip3 install -r requirements.txt
sudo mv /cuba/cuba-transport-monitoring/cuba-transport-monitoring.service /lib/systemd/system/cuba-transport-monitoring.service
sudo systemctl daemon-reload
sudo systemctl enable cuba-transport-monitoring.service
sudo systemctl status cuba-transport-monitoring.service
