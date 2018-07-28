# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grouptb_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_datetime', models.DateTimeField()),
                ('usage', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DetailLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_datetime', models.DateTimeField()),
                ('usage', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('remark', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OperatorToUpYunGroupTB',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('storage_quota', models.IntegerField(default=0)),
                ('remark', models.TextField(blank=True)),
                ('operator', models.ForeignKey(to='upyun_app.Operator')),
            ],
        ),
        migrations.CreateModel(
            name='UpYunGroupTB',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('remark', models.TextField(blank=True)),
                ('grouptb', models.OneToOneField(to='grouptb_app.GroupTB')),
            ],
        ),
        migrations.AddField(
            model_name='operatortoupyungrouptb',
            name='upyungrouptb',
            field=models.ForeignKey(to='upyun_app.UpYunGroupTB'),
        ),
        migrations.AddField(
            model_name='operator',
            name='upyungrouptbs',
            field=models.ManyToManyField(to='upyun_app.UpYunGroupTB', through='upyun_app.OperatorToUpYunGroupTB'),
        ),
        migrations.AddField(
            model_name='detaillog',
            name='upyungrouptb',
            field=models.ForeignKey(to='upyun_app.UpYunGroupTB'),
        ),
    ]
