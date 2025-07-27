#!/bin/bash
# This script helps TE with ssh to targets in test
# Target file of hostnames and IPs - the script finds the necessary
# IP and initiates an SSH connection.
# I have used this by naming the script 'SSH' and moving it to /usr/bin
# so it can be called easily.
# Written By: Kelly Cantrell

MAP_FILE="/etc/sel-hosts"

if [[ -z "$1" ]]; then
    echo "Usage: SSH <location>"
    exit 1
fi

LOCATION="$1"
IP=$(awk -v loc="$LOCATION" '$1 == loc {print $2}' "$MAP_FILE")

if [[ -z "$IP" ]]; then
    echo "Error: Location not found"
    exit 1
fi

exec ssh "kelly.cantrell@$IP"
