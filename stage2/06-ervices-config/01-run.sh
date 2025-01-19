#!/bin/bash -e

source ../stage-vars.sh

###
### GPSD
###
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



### 
### NTPSEC
### 
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

if [ ! -d $LOGDIR ]; then
    mkdir $LOGDIR
fi

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




###
### SHOREWALL
###
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



###
### ENABLE SERVICES
###
on_chroot << EOF
systemctl enable gpsd
systemctl enable ntpsec
systemctl enable shorewall
systemctl enable rc-local
EOF
echo "Services Enabled"




###
### First Boot Service
###   * Resize root file sytem
###   * Kills whiptail
###  * Remove firstboot service
###  * Reboot for resize to take effect
###
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
if [ ! -e "$SERVICELN" ]; then
    ln -s ${SERVICE} ${SERVICELN}
fi
EOF



###
### RF Web Seervice ( Python web service for RF Canning results )
###
WWWRF="wwwrf"
WWWRFAPP="http-server.py"
WWWRFDIR="/opt/${WWWRF}"
WWWRFSERVICE="${WWWRF}.service"

SERVICE="/etc/systemd/system/${WWWRFSERVICE}"
SERVICELN="/etc/systemd/system/multi-user.target.wants/${WWWRFSERVICE}"

ROOTWWWRFDIR="${ROOTFS_DIR}${WWWRFDIR}"
ROOTRFSERVICEFILE="${ROOTFS_DIR}${SERVICE}"
ROOTRFSERVICEFILELN="${ROOTFS_DIR}${SERVICELN}"


if [ ! -d "${ROOTWWWRFDIR}"  ]; then
    mkdir "${ROOTWWWRFDIR}" 
fi
chmod -R 644 "${ROOTWWWRFDIR}"


SCANRESDIR="files/scan_results"
if [ ! -d "${SCANRESDIR}"  ]; then
    # mkdir "${SCANRESDIR}"
    rm files/scan_results/scan_*
fi
cp -rv files/* "${ROOTWWWRFDIR}/"


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
if [ ! -e "$SERVICELN" ]; then
    ln -s ${SERVICE} ${SERVICELN}
fi
export SHELL=/bin/bash
cd ${WWWRFDIR}

if [ -d "./venv"  ]; then
    sudo rm -rf ./venv
fi

python3 -m venv ./venv

./venv/bin/pip3 install psutil
./venv/bin/pip3 install jinja2
./venv/bin/pip3 install pyrtlsdr
./venv/bin/pip3 install numpy
EOF



###
### RC Local ( Need to restart ntpsec to make pps0 work. Why?)
###
FILE="${ROOTFS_DIR}/etc/rc.local"

cat << EOF > $FILE
#!/bin/sh -e
(sleep 40 && sudo systemctl restart ntpsec) &
(sleep 42 && sudo systemctl restart gpsd) &
(sleep 70 && sudo systemctl restart ntpsec) &
(sleep 72 && sudo systemctl restart gpsd) &
exit 0
EOF

chmod +x $FILE



