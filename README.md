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
  * This is where all the credentails for the OS go such as passwords and system name.
* Edit `stage-vars.sh` file for ip addresses and credentials for access point
* At a terminal run `sudo ./build-docker.sh -c stage2/config`
* Transfer the image to a SD card, i.e `dd if=./deploy/year-month-day-name.img of=/dev/sdXXX status=progress bs=4M`

Wollah! a Pi Zero operating system capable of listening to RF signals with millisecond precision.

## Hardware Requirements

* [Pi Zero: PiHut](https://thepihut.com/products/raspberry-pi-zero-wh-with-pre-soldered-header)
* [Pi USB Hat: PiHut](https://thepihut.com/products/4-port-usb-hub-phat-for-raspberry-pi-zero) or any micro USB hub
* [SD Card: PiHut](https://thepihut.com/products/noobs-preinstalled-sd-card)
* [GPS Board: Amazon](https://www.amazon.co.uk/gp/product/B08XGN4YLY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
* [GPS Antenna: Amazon](https://www.amazon.co.uk/gp/product/B01BML4XMQ/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
* [NooElec Nano SDR: Amazon](https://www.amazon.co.uk/gp/product/B01B4L48QU/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&(psc=1))
* [RP-SMA to w.FL / MHF3: Amazon](https://www.amazon.co.uk/TUOLNK-RP-SMA-Coaxial-Antenna-Extension/dp/B0B9RXDLNN/ref=sr_1_1_sspa?crid=1KKU7DIID3CRR&dib=eyJ2IjoiMSJ9.KJDSiFJ-nop6N45mMRKlPI4Op8xYWUON40kLIp09oEvoK4zwYPbR3awLxOM87ZQ9Zf_wTRgB8hnWrFCqgTebE1EZ4EbEnoNUhO3V_gZzpPduU4LH2gUZpYQsDpUJQz4CNnqimkNUr6vFsQi5UlnxY29xK7dxX6HmeINlhm4qfgsaqmSm6D1MhTEEVeNia49dn5hqkY2C0nvUYQ9OWZUF-F3-EAFY5AMTXtdQEJUngmozcLfCPdXeM1_mikvBePZT8wcaWWoQAaRcbVb6zbve0zr62_2leIvQ3ZcGXCyLksQ.iI-XuoRPIpPCO0yuQBnxIgz6deFjaykYV5fPVQ9XI9o&dib_tag=se&keywords=RP-SMA+to+w.FL&qid=1742574783&s=electronics&sprefix=rp-sma+to+w.fl%2Celectronics%2C744&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1)



## Boot up notes

When the system first boots it will resize the hard disk and then reboot.


## Connecting and IP Addresses

### Wifi

To connect via wifi use the credentials in the `stage2/stage-vars.sh` file such as SSID, Password and IP Address.
Once connected via wifi you will then be able to ssh into the device and provide the user name and password contained in the `stage2/config` file.

### Ethernet

If connecting via ethernet you will have to consult your IP address providing system to find out the address of the device.
Once connected via ethernet you will then be able to ssh into the device and provide the user name and password contained in the `stage2/config` file.

## Scanning

The radio frequency scanning is done via a web interface and can be accessed by entering http://<IP_ADDRESS> in a browser. See the wifi or ethernet sections above for obtaining an IP address.

The web interface is still under development and a more detailed description will be given when it becomes more stable.
But the basic idea is to use a JSON file, which can be uploaded via the FAT page, to configure the frequencies to be scanned. This will include the start, stop, step and db levels. The scanning will be done on a 'Scanning' page which will graph the results.


## NTP Service

You can test the stratum1 NTP service from a linux terminal by issuing the following command ...

```bash
ntpq -p <IP ADDRESS>

remote                                   refid      st t when poll reach   delay   offset   jitter
=======================================================================================================
*SHM(1)                                  .PPS0.           0 l    8   64  377   0.0000  -0.0266   0.0048
xSHM(0)                                  .GPS0.           0 l    7   64  377   0.0000 -133.020   0.3808
xPPS(0)                                  .PPS0.           0 l    6   16  377   0.0000  -0.0261   0.0005
```

## GPS monitoring

GPS information can be obtained by ssh'ing into the device and issuing the `gpsmon` command at the terminal. Basic GPS information can be seen on the web interface.

## Routing

The device will act as a wifi router if a  usb->ethernet adapter is plugged in and connected to the internet

## Web Service

A web service exists on port 80 that allows the configuring and scanning of radio frequencies.

Screen shots:

**Home Page**
![Home page](https://www.tgu-ltd.uk/img/rfpost_home_page.png)

**FAT Page**
![FAT page](https://www.tgu-ltd.uk/img/rfpost_fat_page.png)

**Scan Page**
![Scan page](https://www.tgu-ltd.uk/img/rfpost_scan_page.png)

