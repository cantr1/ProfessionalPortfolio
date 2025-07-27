#!/bin/bash
# System Audit Script — No changes made
# Written By: Kelly Cantrell (Audit Version)

STATUS=0 # Tracks pass (0) or fail (1)
echo "🔍 Starting System Hardening Audit..."

# ========== Guest Accounts ==========
if dpkg -l | grep -q lightdm; then
    echo "❌ LightDM is installed."
    STATUS=1
else
    echo "✅ LightDM not installed."
fi

# ========== Root Login ==========
root_shell=$(getent passwd root | cut -d: -f7)
if [ "$root_shell" = "/sbin/nologin" ]; then
    echo "✅ Root login shell set to nologin."
else
    echo "❌ Root login shell is $root_shell."
    STATUS=1
fi

# ========== Root Account Lock ==========
if sudo passwd -S root | grep -q "L"; then
    echo "✅ Root account is locked."
else
    echo "❌ Root account is not locked."
    STATUS=1
fi

# ========== Unnecessary Services ==========
services=(ModemManager bluetooth cups wpa_supplicant brltty speech-dispatcherd alsa-restore alsa-status)
for svc in "${services[@]}"; do
    state=$(systemctl is-enabled "$svc" 2>/dev/null)
    if [[ "$state" == "enabled" ]]; then
        echo "❌ $svc is enabled."
        STATUS=1
    else
        echo "✅ $svc is $state."
    fi
done

# ========== Bluetooth AutoEnable ==========
bt_conf="/etc/bluetooth/main.conf"
if grep -q "AutoEnable=true" "$bt_conf"; then
    echo "❌ Bluetooth AutoEnable is true."
    STATUS=1
else
    echo "✅ Bluetooth AutoEnable is not set to true."
fi

# ========== UID 0 Audit ==========
uid_0s=$(awk -F: '($3 == 0) {printf "%s ",$1}' /etc/passwd)
if [ "$uid_0s" = "root " ]; then
    echo "✅ Only root has UID 0."
else
    echo "❌ Other accounts with UID 0: $uid_0s"
    STATUS=1
fi

# ========== Bloatware ==========
bloat=(thunderbird gnome-mahjongg gnome-mines gnome-sudoku aisleriot)
for app in "${bloat[@]}"; do
    if dpkg -l | grep -q "$app"; then
        echo "❌ $app is installed."
        STATUS=1
    else
        echo "✅ $app is not installed."
    fi
done

# ========== WiFi ==========
nmcli_status=$(nmcli radio wifi 2>/dev/null)
if [ "$nmcli_status" = "disabled" ]; then
    echo "✅ WiFi disabled via NetworkManager."
elif ! sudo systemctl is-active -q NetworkManager; then
    echo "✅ Netplan is managing networking (no NetworkManager WiFi)."
else
    echo "❌ WiFi is enabled."
    STATUS=1
fi

# ========== USB Storage ==========
usb_conf="/etc/modprobe.d/blacklist-usbdrive.conf"
if [ -f "$usb_conf" ]; then
    echo "✅ USB storage block config exists."
else
    echo "❌ USB storage block config is missing."
    STATUS=1
fi

# ========== SSH Configuration ==========
sshd_config="/etc/ssh/sshd_config"

check_ssh() {
    if grep -Eq "$1" "$sshd_config"; then
        echo "✅ SSH: $2"
    else
        echo "❌ SSH: $2 not set correctly."
        STATUS=1
    fi
}

check_ssh "^PermitRootLogin no" "PermitRootLogin no"
check_ssh "^PubkeyAuthentication yes" "PubkeyAuthentication yes"
check_ssh "^MaxAuthTries 3" "MaxAuthTries 3"
check_ssh "^LoginGraceTime 45" "LoginGraceTime 45"

if grep -q "ClientAliveInterval" "$sshd_config"; then
    echo "✅ SSH: ClientAliveInterval is set."
else
    echo "❌ SSH: ClientAliveInterval not set."
    STATUS=1
fi

# ========== Check Status of Drive Encryption ==========
# List all nvme/sd disks and partitions
mapfile -t devices < <(lsblk -rno NAME,TYPE,MOUNTPOINT | awk '$1 ~ /^nvme|^sd/ { print $1 "|" $2 "|" $3 }')

for entry in "${devices[@]}"; do
    IFS="|" read -r name type mountpoint <<< "$entry"

    # Skip /boot and /boot/efi
    if [[ "$mountpoint" == "/boot" || "$mountpoint" == "/boot/efi" ]]; then
        echo "Skipping "$mountpoint partition: /dev/$name"
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

# Final result
if [ "$STATUS" -eq 0 ]; then
    echo "🎉 Audit passed with no findings."
else
    echo "⚠️  Audit completed with issues."
fi

exit $STATUS

