#!/bin/bash
# Check all applicable disks and partitions for LUKS encryption

STATUS=0

# List all nvme/sd disks and partitions
mapfile -t devices < <(lsblk -rno NAME,TYPE,MOUNTPOINT | awk '$1 ~ /^nvme|^sd/ { print $1 "|" $2 "|" $3 }')

for entry in "${devices[@]}"; do
    IFS="|" read -r name type mountpoint <<< "$entry"

    # Skip /boot and /boot/efi
    if [[ "$mountpoint" == "/boot" || "$mountpoint" == "/boot/efi" ]]; then
        echo "Skipping $mountpoint partition: /dev/$name"
        continue
    fi

    # Special message for whole disks
    if [[ "$type" == "disk" && "$name" != *p* ]]; then
        echo "Found whole disk: /dev/$name — whole disks themselves are not encrypted, checking partitions instead..."
        continue
    fi

    # Check encryption status
    if [[ "$type" == "disk" || "$type" == "part" ]]; then
        echo "Checking /dev/$name..."
        if sudo cryptsetup isLuks /dev/$name &>/dev/null; then
            echo "✅ /dev/$name is LUKS encrypted"
        else
            echo "❌ /dev/$name is NOT LUKS encrypted"
            STATUS=1
        fi
    fi
done

exit "$STATUS"
