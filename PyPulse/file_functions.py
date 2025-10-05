# This file contains functions to work with the config file for hosts
import json
import sys
from resources import DEFAULT_CONFIG

def print_host_file(config_file: str) -> None:
    """Prints the hosts json file to the terminal"""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        print(json.dumps(config, indent=2))
    except FileNotFoundError:
        print("ERROR: Unable to locate hosts file inside current directory")
    except FileExistsError:
        print("ERROR: File does not exist")
    except json.JSONDecodeError:
        print("File not valid - likely empty")
    except Exception as e:
        print(f"ERROR: {e}")

def add_host(config_file: str) -> None:
    """Takes user input to create a new host in the json file"""
    try:
        name = input("What is the hostname: ")
        url = input("What is the url: (https://google.com) ")
        host = {"name": name,
                "url": url}
            
        with open(config_file, "r") as f:
            config = json.load(f)
        config["targets"].append(host)
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print("Host successfully added to file")

    except FileNotFoundError:
        print("ERROR: Unable to locate hosts file inside current directory")
    except FileExistsError:
        print("ERROR: File does not exist")
    except json.JSONDecodeError:
        print("File not valid - likely empty")
    except Exception as e:
        print(f"ERROR: {e}")

def remove_host(config_file: str) -> None:
    """Takes user input to create a new host in the json file"""
    try:
        # Print list of hosts
        with open(config_file, "r") as f:
            config = json.load(f)
        
        print("=== Current Hosts ===")
        for host in config["targets"]:
            print(host["name"])
        
        choice = input("Please choose one host to remove: ").lower().strip()

        # Find index to remove
        target_index = 0
        for host in config["targets"]:
            if host["name"].lower().strip() == choice:
                break
            else:
                target_index += 1
        
        # Check that target index is in range before moving forward
        if target_index >= len(host["targets"]):
            print("Failure to find target host...")
            sys.exit(1)
        
        # Remove the key based on index
        del config["targets"][target_index]

        with open(config_file, "w") as f:
             json.dump(config, f, indent=2)

        print("Host successfully removed.\n")

    except FileNotFoundError:
        print("ERROR: Unable to locate hosts file inside current directory")
    except FileExistsError:
        print("ERROR: File does not exist")
    except json.JSONDecodeError:
        print("File not valid - likely empty")
    except KeyError:
        print("Unable to find key in config file")
    except Exception as e:
        print(f"ERROR: {e}")

def generate_default() -> None:
    """Generates default config in default location"""
    try:
        with open("./hosts.json", "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print("Default config successfully written")
    except Exception as e:
        print("ERROR: {e}")

def get_host(config_file: str) -> dict:
    """Allows the user to select a host and returns the full dict of that host"""
    # Print list of hosts
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            
        print("=== Current Hosts ===")
        for host in config["targets"]:
            print(host["name"])
        
        choice = input("Which host would you like to test: ").lower().strip()

        # Find index to remove
        target_index = 0
        for host in config["targets"]:
            if host["name"].lower().strip() == choice:
                break
            else:
                target_index += 1
        
        # Check that target index is in range before moving forward
        if target_index >= len(config["targets"]):
            print("Failure to find target host...")
            sys.exit(1)
            
        return config["targets"][target_index]

    except FileNotFoundError:
        print("ERROR: Unable to locate hosts file inside current directory")
    except FileExistsError:
        print("ERROR: File does not exist")
    except json.JSONDecodeError:
        print("File not valid - likely empty")
    except KeyError:
        print("Unable to find key in config file")
    except Exception as e:
        print(f"ERROR: {e}")