# This script returns the entire bash history of a user
# Written By: Kelly Cantrell
# 7/10/25

USER="kelly.cantrell"
HIST=$(sudo cat /home/$USER/.bash_history 2>/dev/null)
    
echo "Target User: $USER"

if [ -z "$HIST" ]; then
    echo " ❌ No history found..."
    exit 1
else
    echo "✅ Found user history..."
    echo "$HIST"
fi