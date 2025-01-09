#!/bin/bash

set -e

DNSMASQ_IP="10.10.17.1"
DNSMASQ_NET="10.10.17.0/24"
DNSMASQ_START="10.10.17.2"
DNSMASQ_END="10.10.17.255"
HOSTAPD_PASS="gps@pi!9"
HOSTAPD_NAME="stratum1pi"

#######################################################
#
# CMDLINE.TXT
#
#######################################################
CMDLINE_TXT="${ROOTFS_DIR}/boot/firmware/cmdline.txt"
echo "console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 fsck.repair=yes rootwait bcm2708.pps_gpio_pin=18" > "$CMDLINE_TXT" 
echo "cmdline.txt written"

#######################################################
#
# CONFIG.TXT
#
#######################################################
CONFIG_TXT="${ROOTFS_DIR}/boot/firmware/config.txt"
echo "" >> "$CONFIG_TXT"
echo "enable_uart=1" >> "$CONFIG_TXT"
echo "dtoverlay=pi3-disable-bt-overlay" >> "$CONFIG_TXT"
echo "dtoverlay=pi3-miniuart-bt" >> "$CONFIG_TXT"
echo "dtoverlay=disable-bt" >> "$CONFIG_TXT"
echo "dtoverlay=pps-gpio,gpiopin=18" >> "$CONFIG_TXT"
echo "config.txt written"

echo "####################################################"
echo "#"
cat $CONFIG_TXT
echo "#"
echo "####################################################"


#######################################################
#
# /ETC/MODULES
#
#######################################################
MODULES_TXT="${ROOTFS_DIR}/etc/modules"
if [ -f "$MODULES_TXT" ]; then
    echo "pps-gpio" >> "$MODULES_TXT"
else
    echo "/etc/modules not found!"
    exit 1
fi
echo "modules written"



#######################################################
#
# Network Manager Setup ( IP's dnsmasq, hostapd)
#
#######################################################

#######################################################
###  Eth0
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
echo "Eth0 interface written"

#######################################################
###  Wlan0
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
address1=$DNSMASQ_IP/24

[ipv6]
method=disabled
EOF
echo "Wlan0 interface written"


#######################################################
###  Connection Permissions
chmod 600 ${ROOTFS_DIR}/etc/NetworkManager/system-connections/*.nmconnection


#######################################################
###  Dnsmasq
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
echo "dnsmasq written"



#######################################################
###  NetowrkManager.conf
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



#######################################################
#
# DHCPCLIENT ( Accept default route )
#
#######################################################

FILE="${ROOTFS_DIR}/etc/dhcp/dhclient.conf"
sed -i 's/rfc3442-classless-static-routes,//g' $FILE


#######################################################
#
# GPSD
#
#######################################################
FILE="${ROOTFS_DIR}/etc/default/gpsd"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
DEVICES="/dev/ttyAMA0 /dev/pps0"
GPSD_SOCKET="/var/run/gpsd.sock"
GPSD_OPTIONS="-n -G -r -b"
START_DAEMON="true"
USBAUTO="true"
EOF

FILE="${ROOTFS_DIR}/etc/systemd/system/gpsd.socket"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
[Unit]
Description=GPS (Global Positioning System) Daemon Sockets

[Socket]
ListenStream=/var/run/gpsd.sock
ListenStream=[::1]:2947
ListenStream=0.0.0.0:2947
SocketMode=0600

[Install]
WantedBy=sockets.target
EOF


FILE="${ROOTFS_DIR}/lib/systemd/system/gpsd.socket"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
[Unit]
Description=GPS (Global Positioning System) Daemon Sockets

[Socket]
ListenStream=/run/gpsd.sock
ListenStream=[::1]:2947
ListenStream=127.0.0.1:2947
SocketMode=0600

[Install]
WantedBy=sockets.target
EOF
echo "gpsd written"


#######################################################
#
# NTPSEC
#
#######################################################
FILE="${ROOTFS_DIR}/etc/default/ntpsec"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
NTPD_OPTS="-g"
IGNORE_DHCP="yes"
NTPSEC_CERTBOT_CERT_NAME=""
EOF


FILE="${ROOTFS_DIR}/etc/ntpsec/ntp.conf"
DRIFT="${ROOTFS_DIR}/var/lib/ntpsec/ntp.drift"
LOGDIR="${ROOTFS_DIR}/var/log/ntpsec"
mkdir $LOGDIR
if [ -e "$DRIFT" ]; then
    touch $DRIFT
fi
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
driftfile $DRIFT
leapfile /usr/share/zoneinfo/leap-seconds.list
refclock shm unit 1 refid PPS0
refclock shm unit 0 refid GPS0
server 127.127.22.0 minpoll 4 maxpoll 4 iburst
fudge 127.127.22.0 refid PPS0
restrict -4 default kod nomodify limited
restrict 192.168.0.0/8
restrict 10.10.0.0/8
restrict 127.0.0.1
restrict ::1
EOF
echo "ntpsec written"



#######################################################
#
# SHOREWALL
#
#######################################################

FILE="${ROOTFS_DIR}/etc/default/shorewall"
sed -i 's/startup=0/startup=1/g' $FILE

FILE="${ROOTFS_DIR}/etc/shorewall/shorewall.conf"
sed -i 's/IP_FORWARDING=Keep/IP_FORWARDING=Yes/g' $FILE

FILE="${ROOTFS_DIR}/etc/shorewall/interfaces"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
?FORMAT 2
###############################################################################
#ZONE           INTERFACE               OPTIONS
lan             eth0                    dhcp
yfi             wlan0                   dhcp
EOF



FILE="${ROOTFS_DIR}/etc/shorewall/zones"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
###############################################################################
#ZONE           TYPE            OPTIONS         IN_OPTIONS      OUT_OPTIONS
fw              firewall
lan             ip
yfi             ip
EOF



FILE="${ROOTFS_DIR}/etc/shorewall/policy"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
###############################################################################
#SOURCE     DEST    POLICY  LOGLEVEL        RATE    CONNLIMIT
fw          all     ACCEPT
lan         all     ACCEPT
yfi         all     ACCEPT
all         all     REJECT
EOF



FILE="${ROOTFS_DIR}/etc/shorewall/rules"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
######################################################################################################################################
#ACTION     SOURCE      DEST    PROTO   DPORT   SPORT   ORIGDEST    RATE    USER    MARK    CONNLIMIT   TIME    HEADERS SWITCH  HELPER
?SECTION ALL
?SECTION ESTABLISHED
?SECTION RELATED
?SECTION INVALID
?SECTION UNTRACKED
?SECTION NEW
EOF



FILE="${ROOTFS_DIR}/etc/shorewall/snat"
if [ -e "$FILE" ]; then
    touch $FILE
fi
cat << EOF > $FILE
?FORMAT 2
#######################################################################################################################
#ACTION     SOURCE          DEST    PROTO   DPORT   SPORT   IPSEC   MARK    USER    SWITCH  ORIGDEST        PROBABILITY
MASQUERADE  $DNSMASQ_NET   eth0
EOF
echo "shorewall written"


#######################################################
#
# ENABLE SERVICES
#
#######################################################

on_chroot << EOF
systemctl enable gpsd
systemctl enable ntpsec
systemctl enable shorewall
systemctl enable rc-local
EOF
echo "Services Enabled"



#######################################################
#
# First Boot Service
#   * Resize root file sytem
#   * Kills whiptail
#   * Remove firstboot service
#   * Reboot for resize to take effect
#
#######################################################

FBFILE="/etc/default/firstboot.sh"
FBROOTFILE="${ROOTFS_DIR}${FBFILE}"
SERVICE="/etc/systemd/system/firstboot.service"
SERVICELN="/etc/systemd/system/multi-user.target.wants/firstboot.service"
SERVICEFILE="${ROOTFS_DIR}${SERVICE}"

if [ -e "$FBROOTFILE" ]; then
    touch $FBROOTFILE
    chmod +x $FBROOTFILE
fi

if [ -e "$SERVICEFILE" ]; then
    touch $SERVICEFILE
fi


cat << EOF > $FBROOTFILE
#/bin/bash
sudo pkill -9 -f whiptail
sudo chown ntpsec:ntpsec /var/log/ntpsec
sudo raspi-config nonint do_expand_rootfs
sudo raspi-config nonint do_configure_keyboard "Generic 105-key PC"
sudo systemctl disable wpa_supplicant
sudo systemctl disable firstboot.service
sudo rm ${SERVICE}
sudo rm ${FBFILE}
sudo reboot
EOF


cat << EOF > $SERVICEFILE
[Unit]
Description=First Boot Script
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash ${FBFILE}
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

on_chroot << EOF
ln -s ${SERVICE} ${SERVICELN}
EOF

echo "First boot script written"


#######################################################
#
# RF Web Seervice ( Python web service for RF Canning results )
#
#######################################################
WWWRF="wwwrf"
WWWRFAPP="http-server.py"
WWWRFDIR="/opt/${WWWRF}"
WWWRFSERVICE="${WWWRF}.service"

SERVICE="/etc/systemd/system/${WWWRFSERVICE}"
SERVICELN="/etc/systemd/system/multi-user.target.wants/${WWWRFSERVICE}"

ROOTWWWRFDIR="${ROOTFS_DIR}${WWWRFDIR}"
ROOTRFSERVICEFILE="${ROOTFS_DIR}${SERVICE}"
ROOTRFSERVICEFILELN="${ROOTFS_DIR}${SERVICELN}"

mkdir "${ROOTWWWRFDIR}" 
rm files/scan_results/scan_*
cp -rv files/* "${ROOTWWWRFDIR}/"
chmod -R 644 "${ROOTWWWRFDIR}"

if [ -e "$ROOTSERVICEFILE" ]; then
    touch $ROOTSERVICEFILE
fi


cat << EOF > $ROOTRFSERVICEFILE
[Unit]
Description=RFScanning Web Service
After=network.target

[Service]
Type=simple

WorkingDirectory=${WWWRFDIR}
Environment=VIRTUAL_ENV=${WWWRFDIR}/venv
Environment=PATH=${WWWRFDIR}/venv/:$PATH
ExecStart=/bin/bash -c 'source ${WWWRFDIR}/venv/bin/activate && python ${WWWRFAPP}'
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

on_chroot << EOF
ln -s ${SERVICE} ${SERVICELN}
export SHELL=/bin/bash
cd ${WWWRFDIR}
python3 -m venv ./venv
./venv/bin/pip3 install psutil
./venv/bin/pip3 install jinja2
./venv/bin/pip3 install pyrtlsdr
./venv/bin/pip3 install numpy

EOF

echo "RF Web Scan Service written"


#######################################################
#
# RC Local ( Need to restart ntpsec to make pps0 work. Why?)
#
#######################################################

FILE="${ROOTFS_DIR}/etc/rc.local"
cat << EOF > $FILE
#!/bin/sh -e
(sleep 60 && sudo systemctl restart gpsd) &
(sleep 70 && sudo systemctl restart ntpsec) &
(sleep 90 && sudo systemctl restart ntpsec) &
(sleep 110 && sudo systemctl restart ntpsec) &

exit 0
EOF
chmod +x $FILE
echo "RC Local script written"


echo "########################################"
echo "# END OF TGU Config "
echo "# Have a good one "
echo "########################################"

