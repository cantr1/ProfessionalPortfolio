#!/bin/bash
# This script partitions and adds multiple drives to the LVM.
# Args: nvme0n1 nvme1n1 nvme2n1 nvme3n1
# Written by: Kelly Cantrell

# Allow mixed block sizes in /etc/lvm/lvm.conf
sudo sed -i 's/allow_mixed_block_sizes = 0/allow_mixed_block_sizes = 1/' /etc/lvm/lvm.conf

# Loop through all provided drives
for drive in "$@"; do
    selected_drive="/dev/$drive"

    # Check if the drive has no partitions
    line_count=$(lsblk -n $selected_drive -o NAME | wc -l)
    if [ "$line_count" -eq 1 ]; then
        echo "Processing $selected_drive..."
		unpartitioned_drive=$selected_drive

        # Partition the drive
        (
        echo n # Add a new partition
        echo p # Primary partition
        echo 1 # Partition number
        echo   # First sector (Accept default: 1)
        echo   # Last sector (Accept default: varies)
        echo t # Change partition type
        echo 8e # Linux LVM type
        echo w # Write changes
        ) | sudo fdisk $unpartitioned_drive
		echo "$selected_drive has been partitioned..."

        # Re-read partition table (important for automation!)
        sudo partprobe "$unpartitioned_drive"

        # Make filesystem
        sudo mkfs.ext4 "$unpartitioned_drive"p1

        # Create the physical volume
        echo y | sudo pvcreate "$unpartitioned_drive"p1
		echo "Physical volume created..."

        # Extend the volume group
        sudo vgextend vgubuntu "$unpartitioned_drive"p1
		echo "Volume group extended..."

        # Extend the logical volume
        sudo lvextend -l +100%FREE /dev/vgubuntu/root
		echo "Logical volume extended..."

        # Resize the file system
        sudo resize2fs /dev/vgubuntu/root
		echo "File system resized..."

        echo "$selected_drive added to LVM."
	
	# Output if selected drive does not exist	
	elif [ "$line_count" -eq 0 ]; then
		echo "$selected_drive not detected"
    
	# Output if the selected drive is already partitioned
	elif [ "$line_count" -gt 1 ]; then
        echo "$selected_drive is already partitioned. Skipping."
    fi

done

echo "All drives processed."