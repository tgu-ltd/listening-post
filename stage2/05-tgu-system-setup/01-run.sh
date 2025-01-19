#!/bin/bash -e

source ../stage-vars.sh

###
### TGU Specific variables
###
### Need to put this into another/global file 
###

#DNSMASQ_IP="10.10.17.1"
#DNSMASQ_NET="10.10.17.0/24"
#DNSMASQ_START="10.10.17.2"
#DNSMASQ_END="10.10.17.255"
#HOSTAPD_PASS="gps@pi!9"
#HOSTAPD_NAME="stratum1pi"



###
# CMDLINE.TXT
###
CMDLINE_TXT="${ROOTFS_DIR}/boot/firmware/cmdline.txt"
echo "console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 fsck.repair=yes rootwait bcm2708.pps_gpio_pin=18" > "$CMDLINE_TXT" 
echo "cmdline.txt written"



###
# CONFIG.TXT
###
CONFIG_TXT="${ROOTFS_DIR}/boot/firmware/config.txt"
echo "" >> "$CONFIG_TXT"
echo "enable_uart=1" >> "$CONFIG_TXT"
echo "dtoverlay=pi3-disable-bt-overlay" >> "$CONFIG_TXT"
echo "dtoverlay=pi3-miniuart-bt" >> "$CONFIG_TXT"
echo "dtoverlay=disable-bt" >> "$CONFIG_TXT"
echo "dtoverlay=pps-gpio,gpiopin=18" >> "$CONFIG_TXT"
echo "config.txt written"


###
# /etc/modules
###
MODULES_TXT="${ROOTFS_DIR}/etc/modules"
if [ -f "$MODULES_TXT" ]; then
    echo "pps-gpio" >> "$MODULES_TXT"
else
    echo "/etc/modules not found!"
    exit 1
fi


###
###  Eth0
###
FILE="${ROOTFS_DIR}/etc/NetworkManager/system-connections/eth0.nmconnection"
if [ -e "$FILE" ]; then
    touch $FILE
fi


cat << EOF > $FILE
[connection]
id=eth0
type=ethernet
interface-name=eth0
autoconnect=true

[ipv4]
method=auto
never-default=false

[ipv6]
method=disabled
EOF


###
###  Wlan0
###
FILE="${ROOTFS_DIR}/etc/NetworkManager/system-connections/wlan0.nmconnection"
if [ -e "$FILE" ]; then
    touch $FILE
fi



cat << EOF > $FILE
[connection]
id=wlan0
#uuid=d7761840-f729-11ec-b939-1252ac150002
type=wifi
interface-name=wlan0
autoconnect=true

[wifi]
ssid=stratum1
mode=ap
band=bg
channel=6

[wifi-security]
key-mgmt=wpa-psk
psk=$HOSTAPD_PASS

[ipv4]
method=shared
address=$DNSMASQ_IP/24

[ipv6]
method=disabled
EOF



###
###  Connection Permissions
###
chmod 600 ${ROOTFS_DIR}/etc/NetworkManager/system-connections/*.nmconnection




###
###  Dnsmasq
###
FILE="${ROOTFS_DIR}/etc/NetworkManager/dnsmasq.d/dnsmasq.conf"
if [ -f "$FILE" ]; then
    touch "$FILE"
fi

cat << EOF > $FILE
listen-address=127.0.0.1,$DNSMASQ_IP
resolv-file=/etc/resolv.conf
dhcp-authoritative
interface=wlan0
except-interface=eth0
addn-hosts=/etc/hosts
bind-interfaces
domain-needed
bogus-priv
expand-hosts
domain=anant
local=/.anant/
cache-size=1000
dhcp-range=lan,$DNSMASQ_START,$DNSMASQ_END,2h
dhcp-option=lan,121,$DNSMASQ_NET,$DNSMASQ_IP
dhcp-option=lan,option:ntp-server,$DNSMASQ_IP
EOF



###
###  NetowrkManager.conf
###
FILE="${ROOTFS_DIR}/etc/NetworkManager/NetworkManager.conf"
if [ -f "$FILE" ]; then
    touch "$FILE"
fi


cat << EOF > $FILE
[main]
plugins=ifupdown,keyfile

[ifupdown]
#managed=false
managed=true

[device]
#wifi.scan-rand-mac-address=no

EOF
echo "Network Manager written"



###
# DHCPCLIENT ( Accept default route )
###

FILE="${ROOTFS_DIR}/etc/dhcp/dhclient.conf"
sed -i 's/rfc3442-classless-static-routes,//g' $FILE