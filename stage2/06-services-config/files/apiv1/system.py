import time
from datetime import datetime
import subprocess
import json
import psutil




class System:
    def __init__(self):
        pass

    def ten_second(self):
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
    

    def services_poll(self):
        gpsd_status = ''
        wwwrf_status = ''
        ntpsec_status = ''

        try:
            gpsd_status = self.get_status('gpsd')
        except Exception:
            pass

        try:
            ntpsec_status = self.get_status('ntpsec')
        except Exception:
            pass

        try:
            wwwrf_status = self.get_status('wwwrf')
        except Exception:
            pass

        gps = self.get_gps()
        ntp = self.get_ntp()

        return {
            'gpsd': gpsd_status,
            'ntpsec': ntpsec_status,
            'wwwrf': wwwrf_status,
            'lat': gps.get('lat'),
            'lon': gps.get('lon'),
            'sats': gps.get('sat'),
            'ntp': ntp
        }

    def get_status(self, service_name):
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()


    def get_gps(self):
        tpv = None
        sky = None
        ret = {'lat': None, 'lon': None, 'sat': 0}
        try:
            result = subprocess.run(['gpspipe', '-w', '-x 10'], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()
            for line in lines:
                if 'TPV' in line:
                    tpv = json.loads(line)
                    ret['lat'] = tpv.get('lat')
                    ret['lon'] = tpv.get('lon')
                if 'SKY' in line:
                    sky = json.loads(line)
                    for s in sky.get('satellites'):
                        if s.get('used'):
                            ret['sat'] += 1
                if sky is not None and tpv is not None:
                    break
        except Exception as e:
            pass
        return ret


    def get_ntp(self):
        parsed = []
        try:
            result = subprocess.run(['ntpq', '-p'], stdout=subprocess.PIPE, text=True)
            lines = result.stdout.splitlines()
            peer_data = lines[2:]
            for line in peer_data:
                fields = line.split()
                if len(fields) >= 8:
                    parsed.append(fields[0])
        except Exception:
            pass
        return parsed