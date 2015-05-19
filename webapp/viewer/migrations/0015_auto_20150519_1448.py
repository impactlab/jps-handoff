# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0014_auto_20150519_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='abc_phase_rotation',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='current_battery_reading',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='current_season',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='days_on_battery',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='days_since_demand_reset',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='days_since_last_test',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='demand_interval_length',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='early_power_fail_count',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='good_battery_reading',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='service_type_detected',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measurementdatapoint',
            name='times_programmed_count',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
