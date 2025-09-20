#!/bin/bash
# This script sets up the MQTT to allow the server to be a broker
set -e

sudo tee /etc/mosquitto/mosquitto.conf > /dev/null << EOF
listener 1883
allow_anonymous true
EOF

sudo systemctl restart mosquitto

echo "MQTT Now Setup"