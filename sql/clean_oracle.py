#Cleans Oracle CIS export CSVs. 

import re

infile = 'meter_map.csv'
outfile = 'meter_map_cleaned.csv'
pattern = 'UBBCHST'

with open(infile, 'rb') as infh:
    with open(outfile, 'wb') as outfh:
        for line in infh: 
            line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', line)
            if not re.match(pattern,line):
                fields = line.split(';')
                outfields = []
                for field in fields:
                    field = field.lstrip().strip()
                    outfields.append(field)
                if len(outfields[0])>0:
                    outfh.write(','.join(outfields) + '\n')
        
