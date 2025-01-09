# Run this to calculate the default frequency with step size from the original frequency allocation json 

import json
import datetime

from scanner import Scanner

offcom_fat: dict = {}
with open('fat_map/offcom_2018_fat_map.json', 'r') as f:
    offcom_fat = json.loads(f.read())


cd = datetime.datetime.now()
tgu_fat: dict = {
    'author': 'TGU Limited',
    'description': 'Frequency allocation table derived from offcom in the UK 2018',
    'updated': cd.strftime("%d %B %Y"),
    'License': 'MIT',
    'rate': 1024000,
    'gain': 'auto', 
    'bands': []
}


for i, m in enumerate(offcom_fat.get('bands')):
    tgu_fat['bands'].append({
          'id': i,
          'lf': m.get('lf'),    # Lower Frequency Hz
          'uf': m.get('uf'),    # Upper Frequency Hz
          'dn': m.get('s'),     # Description
          'sb': 100,            # Sub Bands Hz
          'db': 0,              # Decibel / Power Level
    })   


with open(Scanner.DEFAULT_FAT_MAP, 'w') as f:
    f.write(json.dumps(tgu_fat, indent=True))