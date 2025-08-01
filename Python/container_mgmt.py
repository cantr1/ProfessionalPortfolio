#!/usr/bin/env python3
# This script passes an argument to all containers present on the server
# I.E. restart, start, stop

import sys
import subprocess

# ==== Functions ====
def get_containers(argument):
    """
    param: argument - str = argument to use with Docker command
    returns: dict = container_id:name pairs
    """
    if argument == 'start':
        command = "docker ps -a | awk '{print $1,$12}' | grep -v CONTAINER"
    else:
        command = "docker ps | awk '{print $1,$12}' | grep -v CONTAINER"

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Only parse stdout
    lines = result.stdout.strip().split('\n')
    containers = {}
    for line in lines:
        if line:  # avoid empty lines
            container_id, name = line.strip().split(maxsplit=1)
            containers[container_id] = name

    return containers


def main(argument, containers) -> None:
    """
    param: argument - str = argument to use with Docker command
    param: containers - dict = collection of containers
    This function passes the argument to all docker containers based on conditional logic
    """
    for cnt in containers:
        command = (f"docker {argument} {cnt}")
        print(f"CID: {cnt} -> Running: {command} on {containers[cnt]}")
        subprocess.run(command, shell=True, capture_output=False)


# ==== Process Input / Call Main ====
if len(sys.argv) < 2:
    print("Usage: python3 container_mgmt.py <argument>")
    sys.exit(1)

if __name__ == "__main__":
    argument: str = sys.argv[1]
    try:
        containers = get_containers(argument)
        main(argument, containers)
    except ValueError:
        print("Please provide a string as an argument...")
    except Exception as e:
        print("Acceptable arguments: 'restart' 'start' 'stop'\n")
        print(f"Error: {str(e)}")