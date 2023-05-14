#!/bin/bash
cp mqtt.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mqtt
systemctl restart mqtt
# sleep 2
# journalctl -n -u mqtt
echo "MQTT Service Install Successed!"

