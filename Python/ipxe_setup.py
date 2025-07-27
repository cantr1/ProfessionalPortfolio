import os
import subprocess
import shutil

# This script sets up iPXE to be run on a server.
# Written by: Kelly Cantrell (7/21/25)

def dir_check(dir):
    """
    Checks if a directory or symlink exists, and removes it if so.
    Returns True if it's safe to create a new symlink.
    """
    if os.path.islink(dir) or os.path.exists(dir):
        print(f"{dir} already exists... removing it")
        try:
            if os.path.islink(dir):
                os.unlink(dir)
            elif os.path.isdir(dir):
                shutil.rmtree(dir)
            else:
                os.remove(dir)
        except Exception as e:
            print(f"Error removing {dir}: {e}")
            return False
    else:
        print(f"{dir} does not exist... Ideal for link creation")
    return True

def link_dir(source, link):
    """
    Creates a symlink from source to link
    """
    if dir_check(link):
        print(f"Creating symlink from {source} to {link}")
        os.symlink(source, link)
        return True
    else:
        raise RuntimeError("Unable to create symlink due to path conflict.")

# ==== Install and Start Apache ====
subprocess.run(['sudo', 'apt', 'install', '-y', 'apache2'], check=True)
subprocess.run(['sudo', 'systemctl', 'start', 'apache2'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'apache2'], check=True)

# ==== Create symlink ====
try:
    link_dir("/tftpboot", "/var/www/html")
except FileExistsError:
    print("Symlink already exists.")
except OSError as e:
    print(f"Failed to create symlink: {e}")
