#!/usr/bin/env python3
# This script processes if Wi-Fi is enabled on a server
# The goal is that it be disabled
# Written by: Kelly Cantrell (7/29/25)
import os
import sys
import subprocess

def check_nmcli():
    """
    :return bool: True if Wi-Fi / radio is disabled --- False otherwise
    """
    command = "sudo radio nmcli wifi"
    result = subprocess.run(command, shell=True, capture_output=True)

    print("Evaluating NetworkManager for Wi-Fi Status")

    if result.returncode == 0:
        return True
    else:
        return False

def eval_wifi_status():
    """
    :return bool: True if Wi-Fi is disabled --- False otherwise
    """
    print("NetworkManager disabled... Evaluating Wi-Fi Status with Netplan Config")

    if os.path.isfile("/etc/netplan/01-network-manager-all.yaml"):
        print("Netplan config found...")
        with open("/etc/netplan/01-network-manager-all.yaml") as f:
            content = f.read()

    if 'wl' in content:
        print("Wireless device found in Netplan Config...")
        return False
    else:
        print("Wireless device not found in Netplan Config...")
        return True

if __name__ == "__main__":
    try:
        if check_nmcli():
            print("Wi-Fi is disabled")
            sys.exit(0)
        else:
            if eval_wifi_status():
                print("Wi-Fi is disabled")
                sys.exit(0)
            else:
                print("Wi-Fi is enabled")
                sys.exit(1)
    except Exception as error:
        print(error)
