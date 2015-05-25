# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grdata',
            name='gr_id',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='grdata',
            name='gr_username',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
