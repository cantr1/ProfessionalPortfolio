import collections
import sys

def open_file(filename):
    with open(filename, "r") as f:
        log = f.readlines()
        return log

def find_types(log_file):
    error_types = []
    for item in log_file:
        error_types.append(item.split(":")[0])
    return error_types

def count_types(log_file):
    error_types = find_types(log_file)
    processed_log = collections.Counter(error_types)
    return processed_log

def display_types(processed_log):
    for item in processed_log:
        print(f"{item}: {processed_log[item]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_log.py <file_path>")
    else:
        log_lines = open_file(sys.argv[1])
        counts = count_types(log_lines)
        display_types(counts)
