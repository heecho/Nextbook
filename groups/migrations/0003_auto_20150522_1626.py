# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20150520_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='avg',
            field=models.IntegerField(blank=True),
        ),
    ]
