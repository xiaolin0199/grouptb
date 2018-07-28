# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operation', models.CharField(max_length=10, choices=[('\u65b0\u589e', '\u65b0\u589e'), ('\u4fee\u6539', '\u4fee\u6539'), ('\u5220\u9664', '\u5220\u9664')])),
                ('model', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField()),
                ('log_datetime', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
