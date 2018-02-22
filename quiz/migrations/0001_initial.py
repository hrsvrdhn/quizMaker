# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-14 07:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('topic', '__first__'),
        ('accounts', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(max_length=2000)),
                ('wrong_answer_1', models.CharField(max_length=500)),
                ('wrong_answer_2', models.CharField(blank=True, max_length=500, null=True)),
                ('wrong_answer_3', models.CharField(blank=True, max_length=500, null=True)),
                ('correct_answer', models.CharField(blank=True, max_length=500, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(max_length=500)),
                ('is_correct', models.BooleanField(default=False)),
                ('candidate', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questionstat', to='accounts.UserProfile')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_history', to='quiz.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Sample Test', max_length=500)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('publish', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='accounts.UserProfile')),
                ('topics', models.ManyToManyField(blank=True, related_name='tests', to='topic.Topic')),
            ],
        ),
        migrations.CreateModel(
            name='TestStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_completed', models.BooleanField(default=False)),
                ('date_taken', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teststat', to='accounts.UserProfile')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='quiz.Test')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.Test'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='quiz.Test'),
        ),
    ]
