# Generated by Django 2.1.7 on 2019-06-14 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0019_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='difficulty',
            field=models.CharField(choices=[('EASY', 'EASY'), ('MEDIUM', 'MEDIUM'), ('HARD', 'HARD')], default='MEDIUM', max_length=6),
        ),
    ]
