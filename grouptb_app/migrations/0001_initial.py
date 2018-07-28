# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroupTB',
            fields=[
                ('group_id', models.IntegerField(serialize=False, primary_key=True, db_column=b'group_id')),
                ('name', models.CharField(max_length=30, db_index=True)),
                ('parent', models.ForeignKey(related_name='child_set', on_delete=django.db.models.deletion.SET_NULL, db_column=b'parent_id', blank=True, to='grouptb_app.GroupTB', null=True)),
            ],
            options={
                'db_table': 'GroupTB',
            },
        ),
    ]
