# Generated by Django 2.0.2 on 2018-06-17 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("quiz", "0017_auto_20180607_0840")]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="message",
            field=models.CharField(blank=True, max_length=1000, null=True),
        )
    ]
