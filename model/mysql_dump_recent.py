#!/usr/bin/env python
import MySQLdb
import csv, sys, os, datetime

datadir = '/data/extract/'
db_user = 'impactlab'
db_pass = ''
db_name = 'impactlab'

with open('meter_list.csv', 'r') as f:
    fcsv = csv.reader(f)
    meters = fcsv.next()

stop_date = datetime.datetime.now()
start_date = stop_date - datetime.timedelta(days=365)
start_date_evt = stop_date - datetime.timedelta(days=30)

conn = MySQLdb.connect(user=db_user, passwd=db_pass, db=db_name, host='127.0.0.1')
cur = conn.cursor()

for meter in meters:
    out_filename = meter + '__' + \
        datetime.datetime.strftime(start_date,'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(stop_date,'%Y-%m-%dT%H%M%S') + '.csv'
    out_filename_evt = 'evt__' + meter + '__' + \
        datetime.datetime.strftime(start_date_evt,'%Y-%m-%dT%H%M%S') + '__' + \
        datetime.datetime.strftime(stop_date,'%Y-%m-%dT%H%M%S') + '.csv'

    cur.execute('SELECT m.meter_id, p.ts, p.kw, p.kva FROM viewer_meter m JOIN viewer_profiledatapoint p ON '+
                'm.id=p.meter_id WHERE m.meter_id=%s AND p.ts > %s AND p.ts <= %s',(meter,start_date,stop_date))
    with open(datadir+out_filename,'w') as f:
        fcsv = csv.writer(f)
        for line in cur:
            if len(line) != 4: continue
            ts = datetime.datetime.strftime(line[1], '%Y/%m/%d %H:%M')
            fcsv.writerow([line[0], ts, line[2], line[3]])

    cur.execute('SELECT m.meter_id, p.ts, p.event FROM viewer_meter m JOIN viewer_eventdatapoint p ON '+
                'm.id=p.meter_id WHERE m.meter_id=%s AND p.ts > %s AND p.ts <= %s',(meter,start_date,stop_date))
    with open(datadir+out_filename_evt,'w') as f:
        fcsv = csv.writer(f)
        fcsv.writerow(['Device Id','Time','Event'])
        for line in cur:
            if len(line) != 3: continue
            ts = datetime.datetime.strftime(line[1], '%Y-%m-%d %H:%M:%S')
            fcsv.writerow([line[0], ts, line[2]])

