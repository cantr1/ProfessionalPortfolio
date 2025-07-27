#!/bin/bash
# This script audits the server with the use of conditionals
# to make the script idempotent
# Written By: Kelly Cantrell

echo "🔐 Starting System Hardening..."

# ========== Disable Guest Accounts ==========
if dpkg -l | grep -q lightdm; then
    sudo apt purge -y lightdm && echo "✅ LightDM removed."
else
    echo "✅ LightDM not installed."
fi

# ========== Disable Root Login ==========
if [ "$(getent passwd root | cut -d: -f7)" != "/sbin/nologin" ]; then
    sudo usermod -s /sbin/nologin root && echo "✅ Root login shell set to no login."
else
    echo "✅ Root login shell already set to nologin."
fi

# ========== Lock Root Account ==========
if ! sudo passwd -S root | grep -q "L"; then
    sudo usermod -L root && echo "✅ Root account locked."
else
    echo "✅ Root account already locked."
fi

# ========== Disable Unnecessary Services ==========
services=(ModemManager bluetooth cups wpa_supplicant brltty speech-dispatcherd)
for svc in "${services[@]}"; do
    if systemctl is-enabled "$svc" &>/dev/null; then
        sudo systemctl disable --now "$svc" && echo "✅ $svc disabled."
    else
        echo "✅ $svc already disabled."
    fi
done

# ========== Disable Audio Services ==========
service=(alsa-restore alsa-status)
for svc in "${services[@]}"; do
    if systemctl is-enabled "$svc" &>/dev/null; then
        sudo systemctl disable --now "$svc" && echo "✅ $svc disabled."
    else
        echo "✅ $svc already disabled."
    fi
done

# ========== Disable Bluetooth AutoEnable ==========
bt_conf="/etc/bluetooth/main.conf"
if grep -q "AutoEnable=true" "$bt_conf"; then
    sudo sed -i 's/AutoEnable=true/AutoEnable=false/' "$bt_conf"
    echo "✅ Bluetooth AutoEnable disabled."
else
    echo "✅ Bluetooth AutoEnable already disabled or not set."
fi

# ========== Ensure Only Root Has UID 0 ==========
uid_0s=$(awk -F: '($3 == 0) {printf "%s ",$1}' /etc/passwd)
if [ "$uid_0s" = "root " ]; then
    echo "✅ PASS: Only root has UID 0."
else
    echo "❌ FAIL: Other accounts with UID 0: $uid_0s"
fi

# ========== Remove Bloatware ==========
bloat=(thunderbird gnome-mahjongg gnome-mines gnome-sudoku aisleriot)
sudo apt purge -y "${bloat[@]}" &>/dev/null && echo "✅ Bloatware removed."

# ========== Disable WiFi or Check Netplan ==========
nmcli_status=$(nmcli radio wifi 2>/dev/null)
if [ "$nmcli_status" = "disabled" ]; then
    echo "✅ WiFi already disabled via NetworkManager."
elif ! sudo systemctl is-active -q NetworkManager; then
    echo "✅ Netplan is managing networking (no NetworkManager WiFi)."
else
    echo "❌ WiFi is enabled — disabling all radios..."
    sudo nmcli radio all off && echo "✅ All radios disabled."
fi

# ========== Block USB Storage ==========
usb_conf="/etc/modprobe.d/blacklist-usbdrive.conf"
if [ ! -f "$usb_conf" ]; then
    sudo tee "$usb_conf" > /dev/null << EOF
# Block USB storage devices
blacklist uas
blacklist usb_storage
EOF
    echo "✅ USB storage blocked."
else
    echo "✅ USB storage already blocked."
fi

# ========== Secure SSH Configuration ==========
sshd_config="/etc/ssh/sshd_config"

sudo sed -i 's/^#*PermitRootLogin .*/PermitRootLogin no/' "$sshd_config"
sudo sed -i 's/^#*PubkeyAuthentication .*/PubkeyAuthentication yes/' "$sshd_config"
sudo sed -i 's/^#*MaxAuthTries .*/MaxAuthTries 3/' "$sshd_config"
sudo sed -i 's/^#*LoginGraceTime .*/LoginGraceTime 45/' "$sshd_config"

if ! grep -q "ClientAliveInterval" "$sshd_config"; then
    sudo tee -a "$sshd_config" > /dev/null << EOF

ClientAliveInterval 300
ClientAliveCountMax 0
EOF
fi

sudo systemctl restart sshd && echo "✅ SSH configuration secured."

echo "✅ System Hardening Complete."