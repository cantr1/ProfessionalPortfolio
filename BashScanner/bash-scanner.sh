#!/bin/bash
#Desc: This script imitates Nmap as an exercise in shell scripting

# Check if the correct number of arguments was passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <host> <port-range>"
    echo "Example: $0 192.168.1.1 1-100"
    exit 1
fi

HOST=$1
PORT_RANGE=$2

# Extract start and end of port range
IFS="-" read START_PORT END_PORT <<< "$PORT_RANGE"

echo "Scanning $HOST from port $START_PORT to $END_PORT ..."

for ((port=$START_PORT; port<=$END_PORT; port++))
do
    # Using nc for port scanning: -z scans without sending data, -w1 sets timeout to 1 second
    nc -zv -w1 $HOST $port &> /dev/null
    if [ "$?" -eq 0 ]; then
        echo "Port $port is open."
    else
        echo "Port $port is closed."
    fi
done
