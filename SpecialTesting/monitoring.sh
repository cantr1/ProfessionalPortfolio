#!/bin/bash
# This script creates a cycle of pinging switches
# and testing ssh connectivity for a set period of time.
# Written By: Kelly Cantrell

# === CONFIGURATION ===

# IP addresses or hostnames to monitor
targets=("192.1.1.1" "192.1.1.10" "192.1.1.20")

# Only test SSH on these targets
ssh_targets=("192.1.1.10" "192.1.1.20")

# SSH credentials - handles in the for loop
#ssh_user="XXX"
#ssh_pass="YYY"

# Interval between runs (in seconds), e.g. 300 = every 5 minutes
interval=300

# Duration of total monitoring (in hours)
duration=24

# Options for mtr and ping
mtr_opts="-rwzbc 100"
ping_duration=5  # seconds for flood ping

# === LOGGING SETUP ===
log_root="./net_logs_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$log_root"
echo "Log directory: $log_root"

# Calculate number of test cycles
runs=$(( (duration * 3600) / interval ))

# === MAIN MONITORING LOOP ===
for (( i=1; i<=$runs; i++ ))
do
  timestamp=$(date +%Y%m%d_%H%M%S)
  echo "Run $i/$runs – $timestamp"

  for target in "${targets[@]}"
  do
    log_dir="$log_root/$target"
    mkdir -p "$log_dir"

    echo "  [MTR] Testing $target..."
    sudo mtr $mtr_opts "$target" > "$log_dir/mtr_${timestamp}.txt" &

    echo "  [PING -f] Testing $target..."
    #sudo timeout "$ping_duration" ping -f "$target" > "$log_dir/pingf_${timestamp}.txt" 2>&1 &
    ping -w "$ping_duration" "$target" > "$log_dir/pingf_${timestamp}.txt" 2>&1 &

  done

  # === SSH TESTS ===
  for ssh_target in "${ssh_targets[@]}"
  do
    ssh_log_dir="$log_root/$ssh_target"
    mkdir -p "$ssh_log_dir"

    # Establish correct credentials
    if [[ "$ssh_target" == "10.63.3.10" ]]; then
        ssh_user="XXX"
        ssh_pass="YYY"
    elif [[ "$ssh_target" == "10.63.3.11" ]]; then
        ssh_user="XXX"
        ssh_pass="YYY"
    elif [[ "$ssh_target" == "10.63.3.19" ]]; then
        ssh_user="XXX"
        ssh_pass="YYY"
    else
        ssh_user="XXX"
        ssh_pass="YYY"
    fi

    echo "  [SSH] Testing SSH to $ssh_target..."
    sudo sshpass -p "$ssh_pass" ssh -q -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$ssh_user@$ssh_target" exit

    if [ $? -eq 0 ]; then
      echo "$timestamp OK: SSH to $ssh_target successful" >> "$ssh_log_dir/ssh_log.txt"
    else
      echo "$timestamp FAIL: SSH to $ssh_target failed" >> "$ssh_log_dir/ssh_log.txt"
    fi
  done

  wait
  echo "⏳ Waiting $interval seconds before next run..."
  sleep "$interval"
done

echo "All tests completed. Logs saved in: $log_root"