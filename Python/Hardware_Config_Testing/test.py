#!/usr/bin/env python3
# This script collects environmental variables
# then performs testing on the unit.

# ==== Import Modules ====
import os
import sys
import subprocess

# ==== Classes ====
# Creating two classes here - in my environment if a server is not RHEL, then it is Ubuntu,
# thus I can create a parent and child class to perform updates with no issues running this script on
# all of my systems
class Server():
    def __init__(self, hostname):
        self.hostname = hostname
    
    def update(self):
        cmd = "sudo apt update -y"
        subprocess.run(cmd, shell=True)

class RedHat(Server):
    def __init__(self, hostname):
        super().__init__(hostname)
    
    def update(self):
        cmd = "sudo dnf update -y"
        subprocess.run(cmd, shell=True)

# ==== Functions ====
def mem_check():
    """
    returns: str - Pass or Fail for the test results
    Script checks if memory is stable and above threshold
    """
    command = 'lsmem | grep "Total online" | cut -d : -f2'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    value = result.stdout.strip()
    number = int(value.rstrip("G"))
    required_memory = 2

    if number >= required_memory:
        return "Pass"
    else:
        return "Fail"
    
def storage_check():
    """
    returns: str - Pass or Fail of the test
    Checks that storage is above a certain threshold
    """
    command = "df -h | grep -E '/$' | awk '{print $5}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    percantage_str = result.stdout.strip().replace('%', '')
    percentage_use = int(percantage_str)
    max_storage = 50 #50% of storage use on root partition

    if percentage_use <= max_storage:
        return "Pass"
    else:
        return "False"
    
def cpu_check():
    command = "arch"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout.strip() == "x86_64":
        return "Pass"
    else:
        return "Fail"

def create_file(path):
    """
    param: path - file path for file containing test info
    Creates the file and writes the first line
    """
    full_path = os.path.join(path, "testfile.txt")
    if os.path.exists(full_path):
        print(f"File path ({path}) already exists...")
    else:
        with open(full_path, "w") as file:
            file.write("Hardware Testing Results\n")
    return full_path

def write_file(test, results, path):
    try:
        with open(path, "a") as file:
            file.write(f"{test}: {results}\n")
        print("Test content written to file...")
    except Exception as e:
        print(f"Error: {e}")

def run_test():
    # First, create the file to store test info
    path = "/home/kelz/Python/"
    create_file(path)

    # Determine distro
    command = "cat /etc/os-release | grep -E '^NAME'"
    distro = subprocess.run(command, shell=True, capture_output=True, text=True)
    hostname = subprocess.run("hostname", shell=True, capture_output=True, text=True)
    if "Red Hat" in str(distro):
        test_srv = RedHat(hostname)
        test_srv.update()
    else:
        test_srv = Server(hostname)
        test_srv.update()

    # Perform tests and write to the test file
    test1 = "Memory Test"
    test2 = "CPU Test"
    test3 = "Storage Test"

    file_path = create_file(path)
    write_file(test1, mem_check(), file_path)
    write_file(test2, cpu_check(), file_path)
    write_file(test3, storage_check(), file_path)

# ==== Main ====
if __name__ == "__main__":
    try:
        run_test()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        raise