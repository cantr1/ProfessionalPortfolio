#!/usr/bin/env python3
# This script moves files from /var/log to an 
# archive directory if they meet certain criteria
# ==== File and Directory Handling ====
import os
import sys
import shutil

# ==== Functions ====
def get_size(directory):
    """
    params: directory - targeted directory
    returns: bool - if files are found
    """
    found = False
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path) and full_path.endswith('.log'):
            size_bytes = os.path.getsize(full_path)
            size_mb = size_bytes / (1024 * 1024)
            if size_mb >= threshold_mb:
                append_list(full_path)
            found = True
    return found

def append_list(x):
    """
    params: x - directory found above threshold
    This function appends items to the list
    """
    found_files.append(x)

def count_list(dir_list):
    """
    param: dir_list - list of found directories
    Prints count of the list if items are found
    """
    total_items = len(dir_list)
    if total_items > 0:
        print(f"Total items found: {len(dir_list)}")
    else:
        print("WARNING: No items found...")

def print_items(found_files):
    """
    param: list of found files
    Prints out the items
    """
    for file in found_files:
        print(file)


def make_archive(archive):
    """
    param: archive - destination directory for archiving
    Created directory if it does not exist
    """
    if not os.path.exists(archive):
        os.mkdir(archive)
        print(f"Directory {archive} created...")
    else:
        print(f"{archive} already exists...")

def archive_files(source, dest_path):
    """
    param: source - file(s) to move
    param: dest_path - destination
    Moves files to the archive directory
    """
    make_archive(dest_path)
    for item in source:
        shutil.move(item, dest_path)
        print(f"Moved {item} to archive...")


# ==== Variables ====
directory = "/var/log"
threshold_mb = 10
found_files = []
archive = "/var/log/archive"

# ==== Main Function ====
if __name__ == "__main__":
    try:
        if get_size(directory):
            print_items(found_files)
            count_list(found_files)
            archive_files(found_files, archive)
            sys.exit(0)
        else:
            print("No files matching criteria...")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
