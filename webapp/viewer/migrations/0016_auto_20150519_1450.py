# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0015_auto_20150519_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='phase_a_dc_detect',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='phase_b_dc_detect',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='phase_c_dc_detect',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
    ]
