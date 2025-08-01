#!/bin/bash
# This script processes the logs generated by the PXE loop.
# Written By: Kelly Cantrell

# === Set Path to Logs === 
LOGDIR="/home/kelly.cantrell/XXX"  

# === For loop to process each file ===
for LOGFILE in "$LOGDIR"/*; do
    # === Declare the log being processed ===
    echo "Processing: $(basename $LOGFILE)"
    echo "==============================="

    # === Grab lines with the transfer data ===
    copy_lines=$(grep "File copied in" "$LOGFILE")

    # === Set variables to track data ===
    sum_time=0
    sum_speed=0
    count=0
    max_time=0

    # === Loop over each matching line ===
    # === IFS preserves spacing; -r prevents backslash escaping ===
    while IFS= read -r line; do
        # === Use regex to grab the time and speed ===
        time=$(echo "$line" | grep -oP 'File copied in \K[0-9.]+')
        speed=$(echo "$line" | grep -oP '@ \K[0-9.]+')

        # === Check that the time and speed variables are valid ===
        if [[ "$time" =~ ^[0-9.]+$ && "$speed" =~ ^[0-9.]+$ ]]; then
            sum_time=$(echo "$sum_time + $time" | bc) # === Use bc for floats ===
            sum_speed=$(echo "$sum_speed + $speed" | bc)

            # === Compare and store max time
            if (( $(echo "$time > $max_time" | bc -l) )); then
                max_time=$time
            fi

            # === Increase the cycle count ===
            ((count++)) 
        fi
    done <<< "$copy_lines"

    # === Calculate averages and display to the terminal ===
    if [[ $count -eq 0 ]]; then
        echo "No valid entries found."
    else
        avg_time=$(echo "scale=2; $sum_time / $count" | bc) # === Round to 2 decimals ===
        avg_speed=$(echo "scale=2; $sum_speed / $count" | bc)
        # === Grab the last cycle completed ===
        total_cycles=$(grep "Completed Cycle" "$LOGFILE" | tail -n 1 | awk '{print $NF}')

        echo "Average File Transfer Time: ${avg_time}s"
        echo "Average File Transfer Speed: ${avg_speed} MB/s"
        echo "Total Cycles Completed: $total_cycles"
        echo "Max Transfer Time: ${max_time}s"
    fi

    echo "==============================="
    echo ""
done
