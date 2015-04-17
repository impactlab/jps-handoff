#!/bin/bash

measurement_file=measurement.csv
dos2unix $measurement_file

python ../jps/manage.py shell <<EOF
from viewer import models
for meter in models.Meter.objects.all():
  try:
    meter._load_measurement_data("$measurement_file")
  except:
    pass

EOF
