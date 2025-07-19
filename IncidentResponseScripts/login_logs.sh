# This script returns the lastlog of all users and checks for specific targets
# Written By: Kelly Cantrell
# 7/11/25

LOG=$(lastlog | grep -v "Never")
STATUS=0

echo "🎯 Beginning User Audit"
echo "=============================================================="

for user in "X" "Y"; do
  echo "🔍 Investigating User Logins ($user)"
  if echo "$LOG" | grep -q "$user"; then
    echo "✅ User found in lastlog --- Displaying data"
    echo "$LOG" | grep "$user"
  else
    echo "❌ User not found in lastlog --- Checking Authentication Logs"
  fi
  
  echo "🔬 Investigating User Authentication Attempts ($user)"
  AUTH=$(sudo cat /var/log/auth.log | grep "user=$user")
  if ! [[ -z "$AUTH" ]]; then
    echo "✅ User found in /var/log/auth.log --- Displaying data"
    echo "$AUTH"
  else
    echo "❌ No authentication history found"
    STATUS=1
  fi

  echo "=============================================================="
done

exit "$STATUS"