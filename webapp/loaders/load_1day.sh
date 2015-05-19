#!/bin/sh
python /home/impactlab/jps-handoff/webapp/manage.py shell <<EOF
from viewer import models
models.update_meter_list()
for m in models.Meter.objects.all():
  print m
  m._load_data_mv90(ndays=1)

EOF
