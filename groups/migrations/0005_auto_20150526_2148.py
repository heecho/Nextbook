# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_book_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='gr_group_id',
            field=models.IntegerField(unique=True),
        ),
    ]
