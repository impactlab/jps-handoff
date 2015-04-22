# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0011_account'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profiledatapoint',
            old_name='kw',
            new_name='kwh',
        ),
    ]
