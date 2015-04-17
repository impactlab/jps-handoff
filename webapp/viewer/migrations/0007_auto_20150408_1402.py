# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0006_meter_on_auditlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='profiledatapoint',
            old_name='kwh',
            new_name='kw',
        ),
        migrations.AddField(
            model_name='meter',
            name='groups',
            field=models.ManyToManyField(to='viewer.Group'),
            preserve_default=True,
        ),
    ]
