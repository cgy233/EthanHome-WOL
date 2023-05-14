#!/bin/bash
systemctl stop mqtt
systemctl disable mqtt
rm /etc/systemd/system/mqtt.service
systemctl daemon-reload
echo "MQTT Service Uninstall Successed!"

