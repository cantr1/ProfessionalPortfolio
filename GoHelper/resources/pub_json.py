#!/usr/bin/env python3
# Script retrieves system data and publishes to Nginx
import json
import psutil
import socket
import time
import os

status = {
    "hostname": socket.gethostname(),
    "uptime_sec": time.time() - psutil.boot_time(),
    "cpu_load": psutil.getloadavg(),  # (1min, 5min, 15min)
    "memory_free_mb": psutil.virtual_memory().available // (1024 * 1024),
    "disk_usage_root": psutil.disk_usage("/").percent,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}

output_file = "/var/www/html/status.json"
with open(output_file, "w") as f:
    json.dump(status, f, indent=2)

os.chmod(output_file, 0o644)  # make sure Nginx can read it
