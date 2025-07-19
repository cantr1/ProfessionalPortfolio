#!/bin/bash
# This script calculates the targeted week for each server and conditionally applies updates
# Written By: Kelly Cantrell

# Get the week # of the month (1–5)
week_num=$(date +%e | awk '{print int(($1-1)/7)+1}')

# Determine Pod Letter from hostname
pod_letter=$(hostname | awk -F- '{print $3}' | cut -c1)

# Map Pod Letter to a target week
case $pod_letter in
  A | M | C)
    target_week=1
    ;;
  L | E | F)
    target_week=2
    ;;
  B | J | K)
    target_week=3
    ;;
  D | O | N)
    target_week=4
    ;;
  *)
    echo "❌ Unrecognized pod letter: $pod_letter. Skipping updates."
    exit 1
    ;;
esac

# Determine if it's the correct week
if [[ "$week_num" -ne "$target_week" ]]; then
  if [[ "$week_num" -eq 5 && "$target_week" -eq 4 ]]; then
    echo "🆗 Week 5, but treated as last Sunday for week 4 pods. Proceeding with updates..."
  else
    echo "❌ Not the correct week ($target_week). Exiting..."
    exit 0
  fi
fi

echo "✅ This is the correct Sunday! Proceeding with updates..."
sudo apt update -y
sudo apt upgrade -y
