#!/bin/bash
# This script processes logs from the switch monitoring script
# Written By: Kelly Cantrell

log_root="$1"

if [ -z "$log_root" ]; then
  echo "❌ Please provide the log directory:"
  echo "   ./evaluate_logs.sh ./net_logs_YYYYMMDD_HHMMSS"
  exit 1
fi

echo "🔍 Evaluating logs in: $log_root"
echo "======================================================================"

for ip_dir in "$log_root"/*; do
  [ -d "$ip_dir" ] || continue
  ip=$(basename "$ip_dir")
  echo "📌 Results for $ip"

  total_loops=0
  for file in "$ip_dir"/mtr_*.txt; do
        ((total_loops++))
  done
  echo "Total Loops = $total_loops"


  # Analyze MTR logs
  mtr_issues=0
  mtr_files=0
  for mtr_file in "$ip_dir"/mtr_*.txt; do
    ((mtr_files++))
    if grep -qE '[1-9][0-9]*\.[0-9]+%|\s[1-9][0-9]?% ' "$mtr_file"; then
      ((mtr_issues++))
    fi
  done
  echo "MTR issues: $mtr_issues files with packet loss out of $mtr_files total files"

  # Analyze Ping logs
  ping_issues=0
  ping_files=0
  for ping_file in "$ip_dir"/pingf_*.txt; do
    ((ping_files++))
    if grep -qiE 'error|unreachable|dropped' "$ping_file" || grep -qE '[1-9][0-9]*% packet loss' "$ping_file"; then
      ((ping_issues++))
    fi
  done
  echo "Ping issues: $ping_issues files with errors out of $ping_files total files"

  # Analyze SSH logs if available
  ssh_log="$ip_dir/ssh_log.txt"
  if [ -f "$ssh_log" ]; then
    ssh_failures=$(grep -c "FAIL" "$ssh_log")
    echo "SSH failures: $ssh_failures failed connections"
  fi

  echo ""
done