#!/bin/bash
# This script checks that CrowdStrike and Trend are active on the server and restarts if needed
# Written by: Kelly Cantrell (6/24/2025)

# === Check that CS is active ===
if sudo systemctl is-active -q falcon-sensor.service; then
    echo "✅ CrowdStrike is active."
else
    echo "❌ CrowdStrike is not active."
    sudo systemctl restart falcon-sensor.service
fi

# === Check that Trend is active ===
if sudo systemctl is-active -q ds_agent.service; then
    echo "✅ Trend is active."
else
    echo "❌ Trend is not active."
    sudo systemctl restart ds_agent.service
fi