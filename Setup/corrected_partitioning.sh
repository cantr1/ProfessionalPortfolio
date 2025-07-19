#!/bin/bash
# This script partitions and adds multiple drives to the LVM.
# Args: nvme0n1 nvme1n1 nvme2n1 nvme3n1
# Written by: Kelly Cantrell

# Corrected version - will likely disuse as this process is generally unwise
# Will need to modify to add second drive to a seperate mount point and encrypt

set -euo pipefail

# Allow mixed block sizes in /etc/lvm/lvm.conf
sudo sed -i 's/allow_mixed_block_sizes = 0/allow_mixed_block_sizes = 1/' /etc/lvm/lvm.conf

for drive in "$@"; do
    selected_drive="/dev/$drive"
    line_count=$(lsblk -n "$selected_drive" -o NAME | wc -l)

    if [ "$line_count" -eq 1 ]; then
        echo "Processing $selected_drive..."
        unpartitioned_drive="$selected_drive"

        (
        echo n     # New partition
        echo p     # Primary
        echo 1     # Partition number
        echo       # Default first sector
        echo       # Default last sector
        echo t     # Change type
        echo 8e    # Linux LVM
        echo w     # Write
        ) | sudo fdisk "$unpartitioned_drive"

        echo "$selected_drive has been partitioned..."

        sudo partprobe "$unpartitioned_drive"

        pv_part="${unpartitioned_drive}p1"

        if sudo pvs | grep -q "$pv_part"; then
            echo "$pv_part already part of LVM. Skipping."
            continue
        fi

        sudo pvcreate --yes "$pv_part"
        echo "Physical volume created..."

        sudo vgextend vgubuntu "$pv_part"
        echo "Volume group extended..."

        sudo lvextend -l +100%FREE /dev/vgubuntu/root
        echo "Logical volume extended..."

        sudo resize2fs /dev/vgubuntu/root
        echo "File system resized..."

        echo "$selected_drive added to LVM."

    elif [ "$line_count" -eq 0 ]; then
        echo "$selected_drive not detected"
    else
        echo "$selected_drive is already partitioned. Skipping."
    fi
done

echo "All drives processed."
