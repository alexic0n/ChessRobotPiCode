#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

echo "Installing Checkmate API as a service"

cp ./checkmate.service /lib/systemd/system/

chmod 644 /lib/systemd/system/checkmate.service

echo "Reloading systemd"

systemctl daemon-reload

echo "Starting service"

systemctl start checkmate
