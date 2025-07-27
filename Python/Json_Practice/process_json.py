# ==== Import json ====
import json
import os

# ==== Read file and store as variable ====
with open("hardware_report.json", "r") as file:
    report = json.load(file)

# ==== Functions ====
def get_hostnames():
    for item in report["devices"]:
        print("HOST: ", item["hostname"])
    
def return_location():
    print("Rack Location: ", report["location"])

def line_in_file():
    print("=======================================")

def line_in_testing():
    print("------")

def clear_terminal():
    os.system('clear')

def network_tests():
    line_in_file()
    print("🛜  NETWORK TESTING")
    x = 0 # variable for formatting output
    for item in report["devices"]:
        print(f"HOST: {item['hostname']}")
        for interface in item["network"]:
            if interface["passed"]:
                print(f"✅ {interface['iface']} PASS --- MAC: {interface['mac']}")
            else:
                print(f"❌ {interface['iface']} FAIL --- MAC: {interface['mac']}")
                print(f" |->  LINK STATE: {interface['link']}")
        x += 1 # Count after each loop
        # Print line in test as long as it is not the last loop
        if x <= len((report["devices"])) - 1:
            line_in_testing() 

def storage_tests():
    line_in_file()
    print("💾 STORAGE TESTING")
    MIN_SSD_SIZE = 500
    MIN_HDD_SIZE = 2000
    x = 0 # variable for formatting output
    for item in report["devices"]:
        print(f"HOST: {item['hostname']}")
        for drive in item["hardware"]["storage"]:
            if drive["type"] == "SSD":
                print(f"DETECTED DEVICE: {drive['device']} --- TYPE: {drive['type']} --- SIZE: {drive['size_gb']}")
                if drive['size_gb'] >= MIN_SSD_SIZE:
                    print("✅ SSD CORRECT SIZE")
                else:
                    print("❌ SSD INCORRECT SIZE")
            elif drive["type"] == "HDD":
                print(f"DETECTED DEVICE: {drive['device']} --- TYPE: {drive['type']} --- SIZE: {drive['size_gb']}")
                if drive['size_gb'] >= MIN_HDD_SIZE:
                    print("✅ HDD CORRECT SIZE")
                else:
                    print("❌ HDD INCORRECT SIZE")
        x += 1 # Count after each loop
        # Print line in test as long as it is not the last loop
        if x <= len((report["devices"])) - 1:
            line_in_testing() 

def hardware_report():
    line_in_file()
    print("⚙️  HARDWARE REPORT")
    x = 0 # variable for formatting output
    for item in report["devices"]:
        print(f"HOST: {item['hostname']}")
        print(f"VENDOR: {item['vendor']}")
        print(f"CPU: {item['hardware']['cpu']['model']} --- {str(item['hardware']['cpu']['cores'])} CORES")
        print(f"RAM: {item['hardware']['memory_gb']}G")
        x += 1 # Count after each loop
        # Print line in test as long as it is not the last loop
        if x <= len((report["devices"])) - 1:
            line_in_testing() 

def production_tests():
    line_in_file()
    print("🚀 PRODUCTION TESTS")
    x = 0 # variable for formatting output
    for item in report["devices"]:
        pass_fail = True
        print(f"HOST: {item['hostname']}")
        for test in item["tests"]:
            result = item["tests"][test]
            if result == "pass":
                print(f"{test}: PASS ✅")
            else:
                print(f"{test}: FAIL ❌")
                pass_fail = False
        if pass_fail:
            print(f"{item['hostname']} PRODUCTION PASS 🎯")
        else:
            print(f"{item['hostname']} PRODUCTION FAIL 🚫")
        x += 1 # Count after each loop
        # Print line in test as long as it is not the last loop
        if x <= len((report["devices"])) - 1:
            line_in_testing() 

# ==== Main ====
clear_terminal()
return_location()
hardware_report()
network_tests()
storage_tests()
production_tests()
line_in_file()
