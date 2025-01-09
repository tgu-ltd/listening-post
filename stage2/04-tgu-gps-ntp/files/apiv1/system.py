import os
import sys
import time
from datetime import datetime
import psutil
import subprocess
import json



class System:

    def __init__(self):
        pass


    def one_second(self):
        current_time_ns = time.time_ns()
        current_time_s = current_time_ns / 1_000_000_000
        now_time = datetime.fromtimestamp(current_time_s)
        load = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        mem = psutil.virtual_memory()
        return {
            'time': now_time.strftime("%d-%m-%Y %H:%M:%S"),
            'cpu': f'{load}% Used',
            'disk': f'{disk.percent}% Used',
            'mem': f'{mem.percent}% Used',
        }
    

    def _get_ntpq(self):
        result = subprocess.run(['ntpq', '-p'], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()

        # Skip the header lines
        peer_data = lines[2:]
        parsed = []

        for line in peer_data:
            fields = line.split()
            if len(fields) >= 8:
                parsed.append({
                    "remote": fields[0],
                    "refid": fields[1],
                    "st": fields[2],
                    "t": fields[3],
                    "when": fields[4],
                    "poll": fields[5],
                    "reach": fields[6],
                    "delay": fields[7],
                })
        return parsed

    def one_minute(self):
        ntpq = self._get_ntpq()
        print(ntpq)
        return ntpq
