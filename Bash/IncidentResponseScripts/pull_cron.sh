# This script returns any cron jobs setup by a user
# Written By: Kelly Cantrell
# 7/11/25

USER="kelly.cantrell"
CRON=$(sudo crontab -u $USER -l 2>/dev/null)
    
echo "Target User: $USER"

if [ -z "$CRON" ]; then
    echo "❌ No cron jobs found..."
    exit 1
else
    echo "✅ Found cron jobs setup by user..."
    echo "$CRON"
fi