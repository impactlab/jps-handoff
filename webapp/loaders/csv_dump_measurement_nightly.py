#!/usr/bin/env python
import datetime, time, csv, sys, os, fnmatch, django
sys.path.append('/home/impactlab/jps-handoff/webapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'jps.settings'
from django.conf import settings
from viewer import models
import pyodbc
django.setup()

d = datetime.datetime.now() - datetime.timedelta(days=2)
d2 = datetime.datetime.now() 

con = pyodbc.connect(servername='mv90', user=os.environ['MV90_USER'],
  password=os.environ['MV90_PASS'], driver='FreeTDS', database='MR-Auxillary')
cur = con.cursor()
cur.execute('SELECT * FROM MeterExtras WHERE ReadingTime >= ? AND ReadingTime < ?', (d,d2))
with open('/data/mv90dump_measurement_nightly.csv', 'w') as f:
  fcsv = csv.writer(f)
  for i,row in enumerate(cur):
    if i % 1000 == 0: print '.'
    fcsv.writerow(row)

with open('/data/mv90dump_measurement_nightly.csv', 'r') as f:
  fcsv = csv.reader(f)
  for row in fcsv:
    try:
      m = models.Meter.objects.get(meter_id=row[2])
    except: continue
    print row[2]
    m._load_measurement_data_mv90(row=row)

