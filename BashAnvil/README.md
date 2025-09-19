# Bash Anvil
.-------..___
  '-._     :_.-'
   .- ) _ ( --.
  :  '-' '-'  ;.
 /'-.._____.-' |
 |   |     \   |
 \   |     /   \
 |   \     )_.-'
 '-._/__..-'

## Overview

Bash Anvil is an end-to-end automation project focused on deploying and hardening Linux systems.
It demonstrates skills in infrastructure provisioning, configuration management, security compliance, and host monitoring.

The project covers the full lifecycle:

- Build Semaphore in a container.

- Configure Semaphore for automation.

- Deploy baseline setup playbooks to endpoints.

- Run automated tests to validate execution.

- Apply server hardening and confirm audit compliance.

- Configure a MQTT broker to receive host updates on a schedule.

## Goals

- Showcase ability to integrate multiple automation tools.

- Deliver hardened and monitored Linux deployments.

- Provide a repeatable framework for secure server builds.

## Components

- Semaphore: job orchestration and playbook execution.

- Ansible: provisioning, configuration, and hardening.

- Bash & Python: scripts for system data collection and reporting.

- MQTT: lightweight monitoring updates from hosts.

## Monitoring Example

Hosts regularly publish JSON status messages (CPU, RAM, disk, network, etc.) to an MQTT topic, providing lightweight telemetry.

```
{
    "Hostname": "DESKTOP-CJA9TI9",
    "OS Version": "Ubuntu 24.04.3 LTS",
    "Kernel": "6.6.87.2-microsoft-standard-WSL2",
    "Uptime": "19:32:39 up  1:58,  1 user,  load average: 0.05, 0.06, 0.07",
    "Total RAM": "14G",
    "CPU Info": {
        "model name": " AMD Ryzen 7 8745HS w/ Radeon 780M Graphics",
        "vendor_id": " AuthenticAMD",
        "cpu cores": " 8",
        "cache size": " 1024 KB",
        "cpu MHz": " 3792.896"
    },
    "Swap Info": {
        "Total Swap": "4.0Gi",
        "Used Swap": "0B",
        "Avaiable Swap": "4.0Gi"
    },
    "Disk Info": {
        "drivers": {
            "Total Size": "931G",
            "Used Space": "420G",
            "Avaiable Space": "511G",
            "Percentage Use": "46%",
            "Mount Point": "/usr/lib/wsl/drivers"
        },
        "/dev/sdd": {
            "Total Size": "1007G",
            "Used Space": "4.8G",
            "Avaiable Space": "951G",
            "Percentage Use": "1%",
            "Mount Point": "/"
        },
        "rootfs": {
            "Total Size": "6.8G",
            "Used Space": "2.7M",
            "Avaiable Space": "6.8G",
            "Percentage Use": "1%",
            "Mount Point": "/init"
        },
        "C:\\": {
            "Total Size": "931G",
            "Used Space": "420G",
            "Avaiable Space": "511G",
            "Percentage Use": "46%",
            "Mount Point": "/mnt/c"
        },
        "tmpfs": {
            "Total Size": "1.4G",
            "Used Space": "20K",
            "Avaiable Space": "1.4G",
            "Percentage Use": "1%",
            "Mount Point": "/run/user/1000"
        }
    },
    "Network Info": {
        "IPV4 Address": "172.22.29.90",
        "MAC Address": "00:15:5d:0e:2b:eb"
    },
    "Virtualization": "wsl"
}
```

Cron job will look like this:

*/10 * * * * mosquitto-pub -t system/info -m "$(python3 /home/kelz/scripts/system_data.py)"
