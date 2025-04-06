#!/bin/bash -e

# This file contains the variables used in the stage2 script.

ETHERNET_IP="eth0"
DNSMASQ_IP="10.10.17.1"
DNSMASQ_NET="10.10.17.0/24"
DNSMASQ_START="10.10.17.2"
DNSMASQ_END="10.10.17.255"
HOSTAPD_PASS="rfpost@dev!01"
HOSTAPD_NAME="rfpost"
HOSTAPD_CHANNEL=6
HOSTAPD_IF="wlan0"
