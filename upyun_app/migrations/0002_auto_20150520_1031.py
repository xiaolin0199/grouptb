# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upyun_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operator',
            options={'verbose_name': '\u64cd\u4f5c\u5458', 'verbose_name_plural': '\u64cd\u4f5c\u5458'},
        ),
        migrations.AlterModelOptions(
            name='operatortoupyungrouptb',
            options={'verbose_name': '\u64cd\u4f5c\u5458\u4e0e\u884c\u653f\u533a\u57df\u7684\u5bf9\u5e94\u5173\u7cfb', 'verbose_name_plural': '\u64cd\u4f5c\u5458\u4e0e\u884c\u653f\u533a\u57df\u7684\u5bf9\u5e94\u5173\u7cfb'},
        ),
        migrations.AlterModelOptions(
            name='upyungrouptb',
            options={'verbose_name': '\u5df2\u5f00\u901aUpYun\u7684\u884c\u653f\u533a\u57df', 'verbose_name_plural': '\u5df2\u5f00\u901aUpYun\u7684\u884c\u653f\u533a\u57df'},
        ),
        migrations.AlterField(
            model_name='operator',
            name='password',
            field=models.CharField(max_length=30, verbose_name=b'\xe5\xaf\x86\xe7\xa0\x81'),
        ),
        migrations.AlterField(
            model_name='operator',
            name='remark',
            field=models.TextField(verbose_name=b'\xe5\xa4\x87\xe6\xb3\xa8', blank=True),
        ),
        migrations.AlterField(
            model_name='operator',
            name='username',
            field=models.CharField(max_length=30, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d'),
        ),
        migrations.AlterField(
            model_name='operatortoupyungrouptb',
            name='operator',
            field=models.ForeignKey(verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe5\x91\x98', to='upyun_app.Operator'),
        ),
        migrations.AlterField(
            model_name='operatortoupyungrouptb',
            name='remark',
            field=models.TextField(verbose_name=b'\xe5\xa4\x87\xe6\xb3\xa8', blank=True),
        ),
        migrations.AlterField(
            model_name='operatortoupyungrouptb',
            name='storage_quota',
            field=models.IntegerField(default=0, verbose_name=b'\xe7\xa9\xba\xe9\x97\xb4\xe9\x85\x8d\xe9\xa2\x9d'),
        ),
        migrations.AlterField(
            model_name='operatortoupyungrouptb',
            name='upyungrouptb',
            field=models.ForeignKey(verbose_name=b'\xe5\xb7\xb2\xe5\xbc\x80\xe9\x80\x9aUpYun\xe7\x9a\x84\xe8\xa1\x8c\xe6\x94\xbf\xe5\x8c\xba\xe5\x9f\x9f', to='upyun_app.UpYunGroupTB'),
        ),
        migrations.AlterField(
            model_name='upyungrouptb',
            name='grouptb',
            field=models.OneToOneField(verbose_name=b'\xe8\xa1\x8c\xe6\x94\xbf\xe5\x8c\xba\xe5\x9f\x9f', to='grouptb_app.GroupTB'),
        ),
        migrations.AlterField(
            model_name='upyungrouptb',
            name='remark',
            field=models.TextField(verbose_name=b'\xe5\xa4\x87\xe6\xb3\xa8', blank=True),
        ),
    ]
