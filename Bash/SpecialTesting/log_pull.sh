#!/bin/bash
# This script pulls the requested file and initiates the logging script
# Intended for use by the Google team on the customer jumper.
# Args: Location File
# Written by: Kelly Cantrell

MAP_FILE="/etc/stellaris_hosts.txt"

if [[ -z "$1" || -z "$2" ]]; then
    echo "Usage: pull_logs <location (Ex. L23)> - <file (Ex. /tmp/dhcp4_L23.txt)>"
    exit 1
fi

LOCATION="$1"
FILE="$2"

IP=$(awk -v loc="$LOCATION" '$1 == loc {print $2}' "$MAP_FILE")

if [[ -z "$IP" ]]; then
    echo "Error: Location not found"
    exit 1
fi


scp "$USER@$IP:$FILE" "/home/$USER/"

# If copy is successful - log event
# Script needs to reference /home if run inside the jail
if [[ "$?" -eq 0 ]]; then
    bash /home/audit_script.sh "$LOCATION" "$IP" "$FILE"
else
    echo "Failed to copy - Transaction not logged."
fi