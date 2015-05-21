#!/usr/bin/env python
import datetime, time, csv, sys, os, fnmatch
sys.path.append('/home/impactlab/jps-handoff/webapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'jps.settings'
from django.conf import settings
from viewer import models
import pyodbc

d = datetime.datetime.now() - datetime.timedelta(days=1)
ds = int(datetime.datetime.strftime(d,'%Y%m%d0000'))
d2 = datetime.datetime.now() 
ds2 = int(datetime.datetime.strftime(d2,'%Y%m%d0000'))

con = pyodbc.connect(servername='mv90', user=os.environ['MV90_USER'],
  password=os.environ['MV90_PASS'], driver='FreeTDS', database='mv90db')
cur = con.cursor()
cur.execute('SELECT * FROM utsProfile WHERE p_dtm >= ? AND p_dtm < ?', (ds,ds2))
with open('/data/mv90dump_nightly.csv', 'w') as f:
  fcsv = csv.writer(f)
  for i,row in enumerate(cur):
    if i % 1000 == 0: print '.'
    fcsv.writerow(row)

meters = {}
for i in models.Meter.objects.all():
  meters[i.meter_id]=i.pk

con = pyodbc.connect(servername='mv90', user=os.environ['MV90_USER'],
   password=os.environ['MV90_PASS'], driver='FreeTDS', database='MR-Auxillary')
cur = con.cursor()

mult = {}
for row in cur.execute('SELECT METER, MULTIPLIER FROM METER_MULTIPLIER'):
  mult[row[0]]=float(row[1])

with open('/data/mv90dump_nightly.csv','r') as f, \
     open('/data/mv90parsed_nightly.csv','w') as g:
  fcsv = csv.reader(f)
  for line in fcsv:
    try: 
      meter_id=meters[line[0]]
      thismult = mult[line[0]]
    except: continue
    raw=float(line[3])*1000
    kwh=float(line[3])*thismult*.0658750031288964
    ts = datetime.datetime.strptime(line[2], '%Y%m%d%H%M')-datetime.timedelta(hours=5)

    tss = datetime.datetime.strftime(ts, '%Y-%m-%d %H:%M:00')
    g.write('"%s",%20.12f,%20.12f,%d\n' % (tss,kwh,raw,meter_id))
