# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-14 11:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("quiz", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="test",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tests",
                to="accounts.UserProfile",
            ),
        )
    ]
