
import time
import os
import threading
from pathlib import Path
import subprocess
import json
import csv
import numpy as np
import shutil
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

Prototype JSON
Usage	Bandwidth	Mode
26.965  - 27.405	CB Radio	            10 kHz / 3 kHz	FM, AM, SSB
118.000 - 136.000	Aviation Airband	    8.33 kHz	AM
163.000 - 168.000	Business Radio (VHF)	12.5 kHz	FM
144.000 - 146.000	Amateur Radio (2m)	    12.5 kHz / 2.7 kHz	FM, SSB
156.000 - 162.000	Marine VHF	25 kHz	FM
380.000 - 400.000	Emergency Services (TETRA)	25 kHz	Digital
430.000 - 440.000	Amateur Radio (70cm)	12.5 kHz / 6.25 kHz	FM, Digital
446.000 - 446.200	PMR446 (Walkie-Talkies)	12.5 kHz	FM, Digital
450.000 - 470.000	Business Radio (UHF)	12.5 kHz	FM, Digital
872.000 - 960.000	Mobile Networks	        200 kHz – 20 MHz	Digital

'''


class Scanner:

    OFFCOM_FAT = 'fat_map/offcom_2018_fat.json'
    ACTIVE_FAT = 'fat_map/active_fat.json'
    CUSTOM_FAT = 'fat_map/custom_fat.json'
    PROTO_FAT = 'fat_map/proto_fat.json'
    SCAN_CSV = 'scan_results/scan.csv'
    FULL_FAT = 'fat_map/full_fat.json'

    SDR_MIN_FREQ = 25000000 # 25MHz, NooElec Nano2. Need a SDR lookup for min, max freq
    SDR_MAX_FREQ = 1700000000 # 1.7Ghz, NooElec Nano2. Need a SDR lookup for min, max freq
    SDR_GAIN = 'auto'
    READ_SAMPLES = 1024
    SDR_SAMPLE_RATE = 2048000

    def __init__(self):
        super().__init__()
        
        self._fat_data = {}
        self._csv_fifo = None
        self._end_freq = None
        self._step_size = None
        self._start_freq = None
        self._active_fat = None
        self.use_trigger = False
        self._scanning_name = None
        self._active_fat_file = None
        
        
        self._csv_fields = ["Seconds", "Name", "Frequency(Hz)", "Power(db)"]
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        self._sdr = RtlSdr()
        self._sdr.gain = Scanner.SDR_GAIN
        self._sdr_gain = Scanner.SDR_GAIN
        self._sdr_min_hz = Scanner.SDR_MIN_FREQ
        self._sdr_max_hz = Scanner.SDR_MAX_FREQ
        self._sdr.sample_rate = Scanner.SDR_SAMPLE_RATE
        self._read_samples = Scanner.READ_SAMPLES
        self.restore_full_fat()

    def _run(self):
        while not self._stop_event.is_set():
            for band in self._fat_data.get('bands'):
                if self._stop_event.is_set(): break

                lf: int = band.get('lower')  # Lower freq
                uf: int = band.get('upper')  # Upper freq
                nm: int = band.get('name')   # Name
                sb: int = band.get('step')   # Step
                db = band.get('db')          # decibel level trigger
                self._scanning_name = nm

                if (lf < self._sdr_min_hz) or (uf > self._sdr_max_hz):
                    continue
                
                for freq in np.arange(lf, uf + sb, sb):
                    if self._stop_event.is_set(): break
                    save = False
                    
                    self._sdr.center_freq = freq
                    #samples = self._sdr.read_samples(256 * 1024)
                    samples = self._sdr.read_samples(num_samples=self._read_samples)
                    power = np.mean(np.abs(samples)**2)
                    avg_power = 10 * np.log10(power)  # Convert to dB

                    if self.use_trigger and avg_power > db:
                        save = True
                    elif not self.use_trigger:
                        save = True
                    
                    if not save:
                        continue

                    ts = int(time.time())
                    entry = {
                        self._csv_fields[0]: ts,
                        self._csv_fields[1]: nm,
                        self._csv_fields[2]: freq,
                        self._csv_fields[3]: round(avg_power, 3)
                    }
                    self._csv_fifo = entry
                    with open(Scanner.SCAN_CSV, mode="a", newline="\n") as csv_file:
                        csv_writer = csv.DictWriter(csv_file, fieldnames=self._csv_fields)
                        csv_writer.writerow(entry)


    def start_thread(self, args: dict = {}):
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self.use_trigger = args.get('use_trigger', False)
        with open(Scanner.ACTIVE_FAT, 'r') as f:
            self._fat_data = json.loads(f.read())

        self._sdr_min_hz = self._fat_data.get('sdr_min_hz', Scanner.SDR_MIN_FREQ)
        self._sdr_max_hz = self._fat_data.get('sdr_max_hz', Scanner.SDR_MAX_FREQ)
        gain = self._fat_data.get('gain', Scanner.SDR_GAIN)
        self._sdr_gain = gain
        self._sdr.gain = gain
        self._sdr.sample_rate = self._fat_data.get('sample_rate', Scanner.SDR_SAMPLE_RATE)
        self._read_samples = self._fat_data.get('read_samples', Scanner.READ_SAMPLES)
        write_header = True

        with open(Scanner.SCAN_CSV, mode="r", ) as f:
            if self._csv_fields[0] in f.readline():
                write_header = False
            
        if write_header:
            with open(Scanner.SCAN_CSV, mode="w", newline="\n") as f:
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



    def clear_scan(self):
        self._csv_fifo = None
        with open(Scanner.SCAN_CSV, "w") as file:
            pass  # This clears the file without writing anything
        return {'ok': True}



    def restore_full_fat(self):
        if self._active_fat != Scanner.FULL_FAT:
            self.stop_thread()
            self.clear_scan()
            self._active_fat = Scanner.FULL_FAT
            self._active_fat_file = Scanner.FULL_FAT
            shutil.copyfile(Scanner.FULL_FAT, Scanner.ACTIVE_FAT)
            
        return {'ok': True}

    def restore_custom_fat(self, bypass=False):
        if self._active_fat != Scanner.CUSTOM_FAT or bypass:
            self.stop_thread()
            self.clear_scan()
            self._active_fat = Scanner.CUSTOM_FAT
            self._active_fat_file = Scanner.CUSTOM_FAT
            shutil.copyfile(Scanner.CUSTOM_FAT, Scanner.ACTIVE_FAT)
        return {'ok': True}
    
    def restore_proto_fat(self):
        if self._active_fat != Scanner.PROTO_FAT:
            self.stop_thread()
            self.clear_scan()
            self._active_fat = Scanner.PROTO_FAT
            self._active_fat_file = Scanner.PROTO_FAT
            shutil.copyfile(Scanner.PROTO_FAT, Scanner.ACTIVE_FAT)
        return {'ok': True}


    def download_full_fat(self):
        data = {}
        with open(Scanner.FULL_FAT, 'r') as f:
            data = json.load(f)
        return data

    def download_proto_fat(self):
        data = {}
        with open(Scanner.PROTO_FAT, 'r') as f:
            data = json.load(f)
        return data


    def upload_custom_fat_file(self, args: dict = {}):
        with open(Scanner.CUSTOM_FAT, 'w') as f:
            f.write(json.dumps(args, indent=True))
        self.restore_custom_fat(bypass=True)
    

    def download_live_file(self):
        data = {}
        for name in self._csv_fields:
            data[name] = []

        with open(Scanner.SCAN_CSV, newline='\n') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                for name, value in row.items():
                    data[name].append(value)
        return data


    def status(self):
        file_size = int(os.path.getsize(Scanner.SCAN_CSV) / 1024)
        running = True if self._thread and self._thread.is_alive() else False
        sdr_rate = '' if not self._sdr else self._sdr.sample_rate
        fifo = '\n  '
        if self._csv_fifo:
            for k, v in self._csv_fifo.items():
                fifo = f'{fifo}{k}:{v}\n  '
        return {
            'fifo': fifo,
            'running': running,
            'datetime': time.strftime("%Y-%m-%d %H:%M:%S"),
            'scan_name': self._scanning_name,
            'sdr_min_hz': self._sdr_min_hz,
            'sdr_max_hz': self._sdr_max_hz,
            'sdr_gain': self._sdr_gain,
            'sdr_rate': sdr_rate,
            'read_samples': self._read_samples,
            'name': Scanner.SCAN_CSV,
            'size': f"{file_size:.2f}KB",
            'fat': self._active_fat_file
        }
    

if __name__ == '__main__':
    sr = Scanner()
    sr.start_thread()
    time.sleep(1)
    sr.status()
    sr.download_live_file()
    #sr.remove_scan_files()
    sr.stop_thread()

