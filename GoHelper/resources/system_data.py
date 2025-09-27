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

def get_misc(data_dict: dict) -> None:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocess to return release info and hostname
    """
    CMD = "hostname"
    hostname = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    data_dict["Hostname"] = hostname.stdout.strip()

    CMD = 'cat /etc/os-release | grep "PRETTY_NAME" | awk -F \'=\' \'{print $2}\' | tr -d \\"'
    os_release = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    data_dict["OS Version"] = os_release.stdout.strip()

    CMD = "uname -r"
    kernel = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    data_dict["Kernel"] = kernel.stdout.strip()

    CMD = "uptime"
    uptime = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    data_dict["Uptime"] = uptime.stdout.strip()



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
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        raw_cpu_dict[key] = value
    
    # Collect desired data the desired dict
    processed_cpu_dict = {}
    desired_values = ["model name\t", "vendor_id\t", "cpu cores\t", "cache size\t", "cpu MHz\t\t"] # Proc info has tabs
    for value in desired_values:
        processed_cpu_dict[value.strip()] = raw_cpu_dict[value]

    data_dict["CPU Info"] = processed_cpu_dict

def get_network_info(data_dict: dict) -> str:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocess to find network information
    """
    network_info = {}

    CMD = "hostname -I"
    hostname = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    network_info["IPV4 Address"] = hostname.stdout.strip()

    CMD = "ip link | grep -A 1 'mq state UP' | grep 'link/ether' | awk '{print $2}'"
    mac = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    network_info["MAC Address"] = mac.stdout.strip()

    data_dict["Network Info"] = network_info

def get_virt_info(data_dict: dict) -> None:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocesses to find active virtualization
    """
    CMD = "systemd-detect-virt"
    virt = subprocess.run(CMD, text=True, shell=True, capture_output=True)
    data_dict["Virtualization"] = virt.stdout.strip()

def get_swap_info(data_dict: dict) -> None:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocesses to find swap info
    """
    CMD = "free -h | grep Swap | awk \'{print $2,$3,$4}\'"
    free = subprocess.run(CMD, shell=True, text=True, capture_output=True)
    total_space, used, available = free.stdout.split()
    data_dict["Swap Info"] = {
        "Total Swap": total_space,
        "Used Swap": used,
        "Avaiable Swap": available
    }

def get_disk_usage(data_dict: dict) -> None:
    """
    :param data_dict: dict - collective dictionary to be modified
    Uses subprocesses to find disk usage on the root partition
    """
    CMD = "df -h | grep -v Filesystem | grep -v none | grep -v snapfuse" # WSL has a ton of fluff that isn't really needed

    # Get the raw data
    disk_data = subprocess.run(CMD, text=True, shell=True, capture_output=True)

    # Process into a dictionary for ease of use
    disk_dict = {}
    for line in disk_data.stdout.splitlines():
        key, total_size, used, available, percent, mount = line.split()
        disk_dict[key] = {
            "Total Size": total_size,
            "Used Space": used,
            "Avaiable Space": available,
            "Percentage Use": percent,
            "Mount Point": mount,
        }

    data_dict["Disk Info"] = disk_dict
        

def main() -> dict:
    # Create an empty dictionary to store data
    system_data = {}

    # Retrieve data and fill in the dict
    get_misc(system_data)
    get_mem_info(system_data)
    get_cpu_info(system_data)
    get_swap_info(system_data)
    get_disk_usage(system_data)
    get_network_info(system_data)
    get_virt_info(system_data)


    # Return json data
    return json.dumps(system_data, indent=4)

if __name__ == "__main__":
    print(main())