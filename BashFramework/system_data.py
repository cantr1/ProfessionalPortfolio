#!/usr/bin/env python3
"""
This script generates system data in JSON format for communication
to the MQTT broker. It is intended to be run as a cron task for 
regular reporting.
"""

import json
import subprocess


def get_mem_info(data_dict: dict) -> None:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocesses to find active memory
    """
    CMD = "lsmem | grep \"Total online memory\" | awk '{print $4}'"
    total_mem = subprocess.run(CMD, text=True, shell=True, capture_output=True)
    data_dict["Total RAM"] = total_mem.stdout.strip()


def get_cpu_info(data_dict: dict) -> str:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocess to find cpu information
    """
    CMD = 'grep -E -A 26 "^processor *\\s: 0" /proc/cpuinfo' # Gets CPU info from proc

    # Get the raw data
    raw_cpu_data = subprocess.run(CMD, text=True, shell=True, capture_output=True)

    # Process into a dictionary for ease of use
    raw_cpu_dict = {}
    for line in raw_cpu_data.stdout.splitlines():
        key, value = line.split(":", 1)
        raw_cpu_dict[key] = value
    
    # Collect desired data the desired dict
    processed_cpu_dict = {}
    desired_values = ["model name\t", "vendor_id\t", "cpu cores\t", "cache size\t", "cpu MHz\t\t"] # Proc info has tabs
    for value in desired_values:
        processed_cpu_dict[value.strip()] = raw_cpu_dict[value]

    data_dict["CPU Info"] = processed_cpu_dict
        

def main() -> None:
    # Create an empty dictionary to store data
    system_data = {}

    # Retrieve data and fill in the dict
    get_mem_info(system_data)
    get_cpu_info(system_data)

    # Convert dict to json
    json_string = json.dumps(system_data, indent=4)

    # Print
    print(json_string)

if __name__ == "__main__":
    main()