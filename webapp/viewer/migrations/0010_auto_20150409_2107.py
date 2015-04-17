# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0009_auto_20150409_1726'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.RemoveField(
            model_name='meter',
            name='user',
        ),
        migrations.AlterField(
            model_name='meter',
            name='metergroups',
            field=models.ManyToManyField(to='viewer.MeterGroup', verbose_name=b'Groups'),
            preserve_default=True,
        ),
    ]
