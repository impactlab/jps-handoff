# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0007_auto_20150408_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='total_usage',
            field=models.FloatField(default=0.0),
            preserve_default=True,
        ),
    ]
