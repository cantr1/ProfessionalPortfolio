#!/bin/bash
# This script sets up tcpdump to run over a set period of time
# Creating pcaps at 5 minute intervals
# Written By: Kelly Cantrell

INTERFACE="ens4f0"
LOG_DIR="/home/kelly.cantrell/tcpdump_logs/"
TOTAL_MINUTES=180   # or: TOTAL_MINUTES="$1"

mkdir -p "$LOG_DIR"
cycles=$(( TOTAL_MINUTES / 5 ))

for ((i = 1; i <= cycles; i++)); do
    timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    tcpdump -i "$INTERFACE" -w "$LOG_DIR/pxe_$timestamp.pcap" -G 300 -W 1 >/dev/null 2>&1
done
