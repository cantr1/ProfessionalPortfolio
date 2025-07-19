# This script returns the sudo commands run by a user
# Written By: Kelly Cantrell
# 7/11/25

USER="kelly.cantrell"
HIST=$(sudo journalctl _COMM=sudo | grep "COMMAND=" | grep "$USER" | cut -d ';' -f 4)
    
echo "Target User: $USER"

if [ -z "$HIST" ]; then
    echo " ❌ No sudo usage found..."
    exit 1
else
    echo "✅ Found sudo usage..."
    echo "$HIST"
fi