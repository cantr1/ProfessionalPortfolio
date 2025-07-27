#!/bin/bash
# This script makes it so that a home directory
# is created for the user upon domain login
# Written By: Kelly Cantrell

# Define the line we want to add
CONFIG_LINE="session required pam_mkhomedir.so skel=/etc/skel/ umask=0077"

# Define the target file
TARGET_FILE="/etc/pam.d/common-session"

# Check if the specific line already exists in the file
if ! sudo grep -F "session required pam_mkhomedir.so" "$TARGET_FILE" > /dev/null 2>&1; then
    # If the line doesn't exist, append it to the file
    echo "$CONFIG_LINE" | sudo tee -a "$TARGET_FILE"
    echo "Configuration line added successfully."
    
    # Restart the service
    sudo systemctl restart systemd-logind
else
    echo "Configuration already exists in $TARGET_FILE. No changes made."
fi