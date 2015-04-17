# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0008_meter_total_usage'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeterGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='meter',
            name='groups',
        ),
        migrations.AddField(
            model_name='meter',
            name='metergroups',
            field=models.ManyToManyField(to='viewer.MeterGroup'),
            preserve_default=True,
        ),
    ]
