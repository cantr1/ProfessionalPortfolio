#!/bin/bash
# This script finds the correct container ID and starts the container
# after an outage
# Written by: Kelly Cantrell (6/16/25)

CID=$(sudo docker ps -a | grep fab | awk '{print $1}')

echo "Starting container"
sudo docker start "$CID"
if [[ $? = 0 ]]; then
    echo "✅ Container started successfully"
else
    echo "❌ Echo error"
fi