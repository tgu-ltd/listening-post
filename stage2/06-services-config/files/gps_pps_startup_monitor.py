"""
Quick script to monitor the NTP service and restart it if it is not locked to a PPS source.
This script is started in /etc/rc.local
"""


import os
import time
import subprocess

CHECK_INTERVAL = 90
PPS_IDENTIFIERS = ["*PPS", "xPPS"]

def monitor():
    locked = False
    while not locked:
        output = subprocess.check_output(["ntpq", "-p"], text=True)
        for peer in output.split("\n"):
            for ident in PPS_IDENTIFIERS:
                if ident in peer:
                    locked = True
                    break
            if locked:
                break

        if not locked:
            os.system("systemctl restart gpsd")
            time.sleep(2)
            os.system("systemctl restart ntpsec")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()