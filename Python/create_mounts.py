# This script can be used to create mount points on a server
# Written by: Kelly Cantrell
import os
import sys
import subprocess

def create_dir(target_path):
    """
    Create a directory if it doesn't exist.
    :param target_path:
    :return: True if the directory was created, False otherwise.
    """
    try:
        if not os.path.exists(target_path):
            os.makedirs(path, exist_ok=True, mode=0o777)
            return True
        else:
            return False
    except OSError:
        print("Creation of the directory failed.")

def create_mount(target_path):
    """
    Create a mount point if it doesn't exist.
    :param target_path:
    :return: True if the mount was created, False otherwise.
    """
    try:
        if not os.path.exists(target_path):
            if create_dir(target_path):
                print("Mount point created.")
            else:
                print("Mount point not created.")
        else:
            print("Mount point already exists.")
        command: str = f'sudo mount -t cifs //x.x.x.x/win_L11 {target_path} -o username="x",password="y",dir_mode=0777,file_mode=0777,rw,vers=2.0'
        result = subprocess.call(command, shell=True)
        if result != 0:
            print("Mount point not created.")
            return False
        else:
            print("Mount point created.")
            return True

    except OSError:
        print("Mount point not created.")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path>")
        sys.exit(1)
    path = sys.argv[1]
    print("Attempting to create mount point: " + path)
    if create_mount(path):
        sys.exit(0)
    else:
        sys.exit(1)
    