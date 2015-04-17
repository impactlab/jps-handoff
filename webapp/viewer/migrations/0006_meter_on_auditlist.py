# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0005_meter_overall_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='on_auditlist',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
