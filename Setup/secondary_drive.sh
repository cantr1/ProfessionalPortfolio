#!/bin/bash
# This script parititions & encrypts the secondary drive and sets up auto unlock at boot via TPM
# Written By: Kelly Cantrell (6/27/2025)

# Exit if a step fails
set -euo pipefail

# ====== Find the target drive - excluding loop devices ======
target_drive=$(lsblk -dn -o NAME,TYPE | while read name type; do
    [[ "$type" != "disk" || "$name" == loop* ]] && continue
    if ! lsblk "/dev/$name" | grep -q '├\|└'; then
        echo "/dev/$name"
    fi
done)

echo "Found Secondary Drive: $target_drive"

echo "Partitioning $target_drive..."
        (
        echo n     # New partition
        echo p     # Primary
        echo 1     # Partition number
        echo       # Default first sector
        echo       # Default last sector
        echo w     # Write
        ) | sudo fdisk "$target_drive"

# ====== Assign variables for encryption process ====== 
partitioned_drive="$target_drive"p1
isolated_drive=$(echo "$partitioned_drive" | cut -d\/ -f3)
mount_point="/mnt/Extra_Storage"
pass_phrase="X" # Password managed in Keypass

# ====== Format the device ======
echo "$pass_phrase" | sudo cryptsetup luksFormat "$partitioned_drive" 

# ====== Open it temporarily ======  
echo "$pass_phrase" | sudo cryptsetup luksOpen "$partitioned_drive" "${isolated_drive}_crypt"
crypt_path="/dev/mapper/${isolated_drive}_crypt"

# ====== Bind the TPM ====== 
echo "$pass_phrase" | sudo clevis luks bind -d "$partitioned_drive" tpm2 '{}' 

# ====== Verify TPM Binding ====== 
sudo clevis luks list -d "$partitioned_drive" 

# ====== Create filesystem on encrypted partition ====== 
sudo mkfs.ext4 "$crypt_path"

# ====== Setup /etc/crypttab ====== 
drive_uuid=$(sudo blkid "$partitioned_drive" | awk '{print $2}' | cut -d\" -f2) 
echo "${isolated_drive}_crypt UUID=$drive_uuid none luks,discard" | sudo tee -a /etc/crypttab

# ====== Setup /etc/fstab and mount point ====== 
sudo mkdir -p "$mount_point"

echo "$crypt_path $mount_point ext4 defaults 0 2" | sudo tee -a /etc/fstab

# ====== Rebuild Initramfs ======
sudo update-initramfs -u 

# ====== Verify Encryption ======
if sudo cryptsetup isLuks "$partitioned_drive" &>/dev/null; then
    echo "✅ "$partitioned_drive" is LUKS encrypted"
else
    echo "❌ "$partitioned_drive" is NOT LUKS encrypted"
fi

# ====== Perform Mount ======
sudo mount -a