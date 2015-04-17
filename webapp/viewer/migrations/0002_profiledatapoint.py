# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileDataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ts', models.DateTimeField()),
                ('kwh', models.FloatField()),
                ('kva', models.FloatField()),
                ('meter', models.ForeignKey(related_name='profile_points', to='viewer.Meter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
