# Generated by Django 2.0.2 on 2018-03-04 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("quiz", "0011_auto_20180304_1529")]

    operations = [
        migrations.AddField(
            model_name="test",
            name="negative_marking",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="teststat",
            name="score",
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True),
        ),
    ]
