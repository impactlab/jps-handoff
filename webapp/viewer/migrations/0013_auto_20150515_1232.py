# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0012_auto_20150421_2246'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profiledatapoint',
            old_name='kva',
            new_name='raw',
        ),
    ]
