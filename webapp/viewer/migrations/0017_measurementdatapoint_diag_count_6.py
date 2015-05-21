# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0016_auto_20150519_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurementdatapoint',
            name='diag_count_6',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
