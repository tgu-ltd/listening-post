# Pi Zero RF Listening Post

This repo is forked from [pi-gen: Tool used to create Raspberry Pi OS images](https://github.com/RPi-Distro/pi-gen) and kept in sync from [TGU Master branch](https://github.com/tgu-ltd/listening-post). Please read the [pi-gen readme](https://github.com/RPi-Distro/pi-gen) for more in depth details on how to build this project.

This branch is used to build a [Raspberry Pi Zero Operating System](https://www.raspberrypi.com/software/) with the following capabilities:

* NTPSec, Stratum1 server using GPS dev board on uart pins and pps on pin 18
* Wifi Access Point with DNS, DHCP services on wlan0
* DHCP client on eth0 when plugged in via a usb->ether adaptor
* IPV4 routing from wlan0 through eth0 if eth0 connected
* HTTP web service for scanning RF frequencies
* SDR RF tools

## How To Build the OS System

* Edit `stage2/config` file with preferred variables. See [pi-gen readme](https://github.com/RPi-Distro/pi-gen) for more details
* Edit `stage-vars.sh` file for ip addresses and credentials for access point
* At a terminal run `sudo ./build-docker.sh -c stage2/config`
* Transfer the image to a SD card, i.e `dd if=./deploy/year-month-day-name.img of=/dev/sdXXX status=progress bs=4M`

Wollah! a Pi Zero operating system capable of listening to RF signals with millisecond precision.

## Hardware Requirements

[Pi Zero: PiHut](https://thepihut.com/products/raspberry-pi-zero-wh-with-pre-soldered-header)
[Pi USB Hat: PiHut](https://thepihut.com/products/4-port-usb-hub-phat-for-raspberry-pi-zero)
[SD Card: PiHut](https://thepihut.com/products/noobs-preinstalled-sd-card)
[GPS Board: Amazon](https://www.amazon.co.uk/gp/product/B08XGN4YLY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
[GPS Antenna: Amazon](https://www.amazon.co.uk/gp/product/B01BML4XMQ/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
[NooElec Nano SDR + Antenna: Amazon](https://www.amazon.co.uk/gp/product/B01B4L48QU/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
[RP-SMA to w.FL / MHF3: Amazon ](https://www.amazon.co.uk/TUOLNK-RP-SMA-Coaxial-Antenna-Extension/dp/B0B9RXDLNN/ref=sr_1_1_sspa?crid=1KKU7DIID3CRR&dib=eyJ2IjoiMSJ9.KJDSiFJ-nop6N45mMRKlPI4Op8xYWUON40kLIp09oEvoK4zwYPbR3awLxOM87ZQ9Zf_wTRgB8hnWrFCqgTebE1EZ4EbEnoNUhO3V_gZzpPduU4LH2gUZpYQsDpUJQz4CNnqimkNUr6vFsQi5UlnxY29xK7dxX6HmeINlhm4qfgsaqmSm6D1MhTEEVeNia49dn5hqkY2C0nvUYQ9OWZUF-F3-EAFY5AMTXtdQEJUngmozcLfCPdXeM1_mikvBePZT8wcaWWoQAaRcbVb6zbve0zr62_2leIvQ3ZcGXCyLksQ.iI-XuoRPIpPCO0yuQBnxIgz6deFjaykYV5fPVQ9XI9o&dib_tag=se&keywords=RP-SMA+to+w.FL&qid=1742574783&s=electronics&sprefix=rp-sma+to+w.fl%2Celectronics%2C744&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1)

## Boot up notes

When the system first boots it will resize the hard disk and then reboot

## Development notes

Still under development:

* NTPSec access and security
* Test Suite to be added to repo to test builds
* Pi0-2, pi4 and Pi5 versions to be added