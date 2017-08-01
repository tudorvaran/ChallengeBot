# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-11 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='challengers',
            field=models.ManyToManyField(to='web.Challenger'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='winner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='web.Source'),
        ),
    ]