# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 00:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dropme', '0003_auto_20160524_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_date',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]