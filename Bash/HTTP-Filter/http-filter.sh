#!/bin/bash
# Author: Kelly Cantrell
# Date: 8/13/24
# This script displays log data based on HTTP methods and status codes
clear

# Displays an overview of the access log
echo "Total Requests: $(wc -l < access.log)"
echo "GET Requests: $(grep "GET " access.log | wc -l)"
echo "POST Requests: $(grep "POST " access.log | wc -l)"
echo "404 Errors: $(grep " 404 " access.log | wc -l)"
echo "DELETE Requests: $(grep "DELETE" access.log | wc -l)"

# Create while-loop
i=1
while [ $i -eq 1 ]
do
    echo "----------------------------------------------"
    # Allows user to query data based on HTTP method
    echo
    echo "To view detailed information based on HTTP method, type the method to query below: (N to exit)"
    read user_input

    echo "----------------------------------------------"
    if [ "$user_input" = "N" ]; then
        i=0
        echo "Goodbye"
    else
        grep "$user_input" access.log
    fi
done
