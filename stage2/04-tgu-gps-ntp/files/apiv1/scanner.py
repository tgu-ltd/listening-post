
import time
import os
import threading
from pathlib import Path
import subprocess
import json
import re
import csv
import numpy as np
import glob

from rtlsdr import RtlSdr


import logging
# Set logging to suppress messages below error level
logging.basicConfig(level=logging.ERROR)


'''
# FAT will look like...
{
    'author': 
    'description': 
    'updated':
    'scan_rate': 
    'bands: [
        {
            'id': 0,     # Identification
            lf: 100,     # Lower Frequency
            uf: 1000,    # Upper Frequency
            sb: 100,     # Subbands
            db: 1, # DB Level 
            dn: 'Example1'
        },
        {
            'id': 1,
            ...
        }
}
'''


class Scanner:

    DEFAULT_FAT_MAP = 'fat_map/tgu_fat_map.json'


    def __init__(self):
        super().__init__()
        self.scan_ids = []
        self.use_trigger = False
        self._fat_data = {}
        self._csv_file = None
        self._end_freq = None
        self._step_size = None
        self._start_freq = None
        self._csv_file_path = None
        self._csv_fifo = None
        self._tgu_fat_file = Scanner.DEFAULT_FAT_MAP

        self._csv_fields = ["Timestamp(ns)", "BandId", "Frequency(Hz)", "Power(db)"]
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        self._sdr = RtlSdr()
        self._sdr.gain = 'auto'
        self._sdr.sample_rate = 2048000
        self._scan_results_dir = 'scan_results'

    def _run(self):
        
        while not self._stop_event.is_set():
            for band in self._fat_data.get('bands'):
                if self._stop_event.is_set(): break
                if self.scan_ids:
                    if band.get('id') not in self.scan_ids:
                        continue

                lf: int = band.get('lf')    # Lower freq
                uf: int = band.get('uf')    # Upper freq
                sb: int = band.get('sb')    # Sub band
                db = band.get('db')         # decibel level trigger
                
                for freq in np.arange(lf, uf + sb, sb):
                    if self._stop_event.is_set(): break
                    save = False
                    
                    self._sdr.center_freq = freq
                    samples = self._sdr.read_samples(256 * 1024)
                    power = np.mean(np.abs(samples)**2)
                    avg_power = 10 * np.log10(power)  # Convert to dB
                    band_id =  band.get('id')

                    if self.use_trigger and avg_power > db:
                        save = True
                    elif not self.use_trigger:
                        save = True
                    
                    if not save:
                        continue

                    ts = time.time_ns() // 1_000_000
                    entry = {
                        self._csv_fields[0]: ts,
                        self._csv_fields[1]: band_id,
                        self._csv_fields[2]: freq,
                        self._csv_fields[3]: round(avg_power, 3)
                    }
                    self._csv_fifo = entry
                    with open(self._csv_file, mode="a", newline="\n") as csv_file:
                        csv_writer = csv.DictWriter(csv_file, fieldnames=self._csv_fields)
                        csv_writer.writerow(entry)


    def start_thread(self, args: dict = {}):
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self.scan_ids = args.get('scan_ids')
        self.use_trigger = args.get('use_trigger', False)
        ids = re.sub(r'[\[\] \s]', '', str(self.scan_ids))
        ids = ids.replace(',', '_')
        with open(self._tgu_fat_file, 'r') as f:
            self._fat_data = json.loads(f.read())

        self._sdr.gain = self._fat_data.get('gain', 'auto') 
        self._sdr.sample_rate = self._fat_data.get('rate', 2048000) 

        self._csv_file = f'{self._scan_results_dir}/scan_{time.time()}_{ids}.csv'
        self._csv_file_path = Path(self._csv_file)
        with open(self._csv_file, mode="w", newline="\n") as f:
            writer = csv.DictWriter(f, fieldnames=self._csv_fields)
            writer.writeheader()

        self._thread = threading.Thread(target=self._run)
        self._thread.start()


    def stop_thread(self):
        if self._thread and self._thread.is_alive():
            self._csv_fifo = None
            self._stop_event.set()
            self._thread.join()
            self._fat_data = {}
            self._thread = None
        return {'ok': True}


    def remove_scan_files(self):
        keep = self._csv_file.replace('{self._scan_results_dir}/', '')
        for file in glob.glob(f"{self._scan_results_dir}/*.csv"):
            if keep in file:
                continue
            os.remove(file)
        return {'ok': True}


    def restore_default_fat(self):
        subprocess.run(['python', 'apiv1/compute_fat.py'])
        return {'ok': True}
    

    def download_fat_file(self):
        data = {}
        with open(Scanner.DEFAULT_FAT_MAP, 'r') as f:
            data = json.load(f)
        return data


    def upload_fat_file(self, args: dict = {}):
        print("uploading")
        with open(Scanner.DEFAULT_FAT_MAP, 'w') as f:
            f.write(json.dumps(args, indent=True))
            print("uploaded")


    def get_scan_files(self):
        files = sorted(glob.glob(f"{self._scan_results_dir}/*.csv"))[::-1]
        return { 'files':  files}


    def get_live_data(self):
        data = []
        with open(self._csv_file, 'r') as f:
            data = f.readlines()[:10]
        return data
    

    def download_live_file(self):
        data = {}
        for name in self._csv_fields:
            data[name] = []

        with open(self._csv_file, newline='\n') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                for name, value in row.items():
                    data[name].append(value)
        return data


    def status(self):
        file_size = self._csv_file_path.stat().st_size / 1024
        running = True if self._thread and self._thread.is_alive() else False
        fifo = '\n  '
        if self._csv_fifo:
            for k, v in self._csv_fifo.items():
                fifo = f'{fifo}{k}:{v}\n  '
        return {
            'fifo': fifo,
            'running': running,
            'name': self._csv_file,
            'size': f"{file_size:.2f}KB",
        }
    

if __name__ == '__main__':
    sr = Scanner()
    sr.start_thread()
    time.sleep(1)
    sr.status()
    sr.download_live_file()
    sr.get_live_data()
    #sr.remove_scan_files()
    sr.stop_thread()

