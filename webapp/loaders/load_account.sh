#!/bin/bash

datadir=/data/cis/
datafile=accounts.csv

accounts_file=${datadir}${datafile}

python /home/tplagge/jps-ntl/jps/manage.py shell <<EOF
from viewer import models
for meter in models.Meter.objects.all():
  meter._load_account_data("$accounts_file")

EOF
