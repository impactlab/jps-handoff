#!/bin/sh
python /home/impactlab/jps-handoff/webapp/manage.py shell <<EOF
import csv
from viewer import models

with open('/data/predictions.csv','r') as f:
  fcsv = csv.reader(f)
  for row in fcsv:
    meter_id = row[0]
    score = row[1]
    try:
      m = models.Meter.objects.get(meter_id=meter_id)
    except:
      continue
    m.overall_score = float(score)
    m.save()

EOF
