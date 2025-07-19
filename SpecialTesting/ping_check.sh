#!/bin/bash
# This script is a quick check to see if a list of IPs
# currently have ping
# Written By: Kelly Cantrell

declare -A SERVERS=(
  [Server1]="10.1.1.1"
  [Server2]="10.1.1.1"
  [Server3]="10.1.1.1"
  [Server4]="10.1.1.1"
  [Server5]="10.1.1.1"
  [Server6]="10.1.1.1"
  [Server7]="10.1.1.1"
  [Server8]="10.1.1.1"
  [Server9]="10.1.1.1"
)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2"
}

for server in "${!SERVERS[@]}"; do
    ip="${SERVERS[$server]}"
    name="$server"
    log "$name" "🤖 Trying ping w/ $server"

    # Ping check with retry
    max_ping_tries=5
    ping_success=0

    for ((i=1; i<=max_ping_tries; i++)); do
        if ping -c 1 "$ip" &>/dev/null; then
            log "$name" "✅ $ip is reachable."
            ping_success=1
            break
        else
            log "$name" "⏳ Attempt $i: $ip not reachable..."
            sleep 5
        fi
    done

    if [ "$ping_success" -eq 0 ]; then
        log "$name" "❌ $ip unreachable after $max_ping_tries attempts. Moving on."
        continue
    fi
done