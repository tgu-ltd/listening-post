import json
import datetime

from scanner import Scanner

offcom_fat: dict = {}
with open(Scanner.OFFCOM_FAT, 'r') as f:
    offcom_fat = json.loads(f.read())


cd = datetime.datetime.now()
full_fat: dict = {
    'author': 'TGU',
    'description': 'Frequency allocation table derived from OffCom band plan 2018',
    'updated': cd.strftime("%d %B %Y"),
    'License': 'MIT',
    'sample_rate': 2048000,
    'read_samples': 1024,
    'gain': 'auto', 
    'sdr_min_hz': 25000000, 
    'sdr_max_hz': 1700000000,
    'bands': []
}


for i, m in enumerate(offcom_fat.get('bands')):
    full_fat['bands'].append({
          'lower': m.get('lf'),   # Lower Frequency Hz
          'upper': m.get('uf'),   # Upper Frequency Hz
          'name': m.get('s'),     # Description
          'step': 100,            # Step/sub band Hz
          'db': 0,                # Decibel Level trigger
    })   


with open(Scanner.FULL_FAT, 'w') as f:
    f.write(json.dumps(full_fat, indent=True))