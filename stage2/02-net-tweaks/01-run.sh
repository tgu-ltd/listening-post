#!/bin/bash -e

mkdir -p "${ROOTFS_DIR}/var/lib/systemd/rfkill/"
echo 0 > "${ROOTFS_DIR}/var/lib/systemd/rfkill/platform-3f300000.mmcnr:wlan"
echo 0 > "${ROOTFS_DIR}/var/lib/systemd/rfkill/platform-fe300000.mmcnr:wlan"