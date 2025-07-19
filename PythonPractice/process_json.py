import json

# Load the json file
with open("hardware_report.json", "r") as file:
    report = json.load(file)

# State the rack location
print("""
██╗  ██╗ █████╗ ██████╗ ██████╗ ██╗    ██╗ █████╗ ██████╗ ███████╗    ████████╗███████╗███████╗████████╗███████╗
██║  ██║██╔══██╗██╔══██╗██╔══██╗██║    ██║██╔══██╗██╔══██╗██╔════╝    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔════╝
███████║███████║██████╔╝██║  ██║██║ █╗ ██║███████║██████╔╝█████╗         ██║   █████╗  ███████╗   ██║   ███████╗
██╔══██║██╔══██║██╔══██╗██║  ██║██║███╗██║██╔══██║██╔══██╗██╔══╝         ██║   ██╔══╝  ╚════██║   ██║   ╚════██║
██║  ██║██║  ██║██║  ██║██████╔╝╚███╔███╔╝██║  ██║██║  ██║███████╗       ██║   ███████╗███████║   ██║   ███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚══════╝                                   
""")

print(f"==== Testing Location ====\n", report["location"])

# Loop through each device and print the hostname
print("\n==== Hardware Units Tested ====")
for item in report["devices"]:
    print("HOSTNAME: ", item["hostname"])

# Print all Stages that have failed for each host
print("\n==== Test Station Results ====")
for item in report["devices"]:
    print("HOSTNAME: ", item["hostname"])
    for test in item["tests"]:
        result=item["tests"][test]
        if result == "pass":
           print(f"✅ {test} Passed")
        else:
           print(f"❌ {test} Failed")
    print ("----")


# Print MAC's of NIC's that passed
print("\n==== Results of Network Interface Testing ====")
for item in report["devices"]:
    print("HOSTNAME: ", item["hostname"])
    for interface in item["network"]:
        if interface["passed"]:
            print("INTEFACE: ", interface["iface"])
            print("MAC ADDRESS: ", interface["mac"])
            print("✅ PASS")
            print ("----")
        else:
            print("INTEFACE: ", interface["iface"])
            print("MAC ADDRESS: ", interface["mac"])
            print("❌ FAIL")
            print ("----")

# Print Hostname, Storage Device, and Total Storage Size
print("\n==== Storage Devices ====")
for item in report["devices"]:
    print("HOSTNAME: ", item["hostname"])
    total_storage=0
    for ssd in item["hardware"]["storage"]:
        total_storage += int(ssd["size_gb"])
        print(f"Device name: {ssd['device']} --- Storage Size: {ssd['size_gb']}G")
    # Convert storage size for GB to TB
    print(f"Total Storage: {total_storage / 1000}T")
    print ("-------------------")