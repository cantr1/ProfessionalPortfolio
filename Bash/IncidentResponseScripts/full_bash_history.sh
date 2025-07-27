#!/bin/bash
# This script returns the bash history of all users
# Written By: Kelly Cantrell
# 4/21/25

for dir in /home/*; do
    USERHOME="$dir"
    USER="${dir:6}"
    
    echo "----------------------------------------------------------------------------------"
    echo "🔍 Found User: $USER"
    echo "Their history:"

    if [ -f "$USERHOME/.bash_history" ]; then
        sudo cat "$USERHOME/.bash_history"
    else
        echo "❌ No .bash_history file found for $USER"
    fi

    echo "----------------------------------------------------------------------------------"
    echo ""
done
