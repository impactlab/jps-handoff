#!/bin/bash
python ../manage.py shell <<EOF
from viewer import models
for i in models.Meter.objects.all():
  print i
  i.update_total_usage()
  i.save()

EOF
