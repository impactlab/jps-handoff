# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0003_measurementdatapoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ts', models.DateTimeField()),
                ('event', models.CharField(max_length=200)),
                ('meter', models.ForeignKey(related_name='events', to='viewer.Meter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
