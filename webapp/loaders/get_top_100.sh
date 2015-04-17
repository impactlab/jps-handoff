#!/bin/sh
python ../manage.py shell <<EOF
import csv
import numpy as np
from viewer import models

m = models.Meter.objects.order_by('-overall_score')
strikerate = [i.meter_id for i in m][0:100]

s = [i.overall_score*i.total_usage for i in m]
recoveramount = [m[i].meter_id for i in np.argsort(s)[::-1]][0:100]

with open('top100_strikerate.csv','w') as f:
  fcsv = csv.writer(f)
  for i in strikerate:
    fcsv.writerow([i])

with open('top100_recoveramount.csv','w') as f:
  fcsv = csv.writer(f)
  for i in recoveramount:
    fcsv.writerow([i])

EOF
