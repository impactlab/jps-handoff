# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0004_eventdatapoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='overall_score',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
    ]
