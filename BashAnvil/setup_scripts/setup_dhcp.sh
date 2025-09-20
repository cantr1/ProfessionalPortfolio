#!/bin/bash

IP=$(hostname -I | awk '{print $1}')

THIRD_OCTET=$(echo "$IP" | cut -d '.' -f1-3)

ACTIVE_INTERFACE=$(sudo nmcli con show | grep ethernet | awk '{print $6}')

sudo tee /etc/dhcp/dhcpd.conf > /dev/null << EOF
subnet $THIRD_OCTET.0 netmask 255.255.255.0 {
  range 192.168.1.100 192.168.1.200;
  option routers $IP;
  option domain-name-servers 8.8.8.8, 8.8.4.4;
  default-lease-time 600;
  max-lease-time 7200;
}
EOF

sed -i "s/INTERFACESv4=""/INTERFACESv4=$ACTIVE_INTERFACE/" /etc/default/isc-dhcp-server

sudo systemctl restart isc-dhcp-server

echo "DHCP Now Setup"