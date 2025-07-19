#!/bin/bash
# This script checks that CrowdStrike and GRR are active on the server
# Written by: Kelly Cantrell (6/12/2025)

# === Variables ===
STATUS=0  # used to track failure
GAGENT_PROCESS=$(pgrep -f gagent)  # grabs the GRR process - pgrep to not grab the grep process

# === Check that CS is active ===
if sudo systemctl is-active -q falcon-sensor.service; then
    echo "✅ CrowdStrike is active."
else
    echo "❌ CrowdStrike is not active."
    STATUS=1
fi

# === Check that Trend is active ===
if sudo systemctl is-active -q ds_agent.service; then
    echo "✅ Trend is active."
else
    echo "❌ Trend is not active."
    STATUS=1
fi

# === Check that GRR has an active process ===
if [[ -n "$GAGENT_PROCESS" ]]; then
    echo "✅ GRR is actively running."
else
    echo "❌ GRR is not running."
    STATUS=1
fi

# === Check the status and provide exit code ===
if [[ "$STATUS" = 0 ]]; then 
    echo "🚀 All services running!"
else
    echo "🪳 One or more services are not running."
fi

exit "$STATUS"
