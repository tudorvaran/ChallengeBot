# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-13 13:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_auto_20170513_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='language',
            field=models.CharField(choices=[('PY2', 'Python2'), ('PY3', 'Python3')], default='PY2', max_length=20),
        ),
        migrations.AlterField(
            model_name='source',
            name='selected',
            field=models.BooleanField(default=0),
        ),
    ]
