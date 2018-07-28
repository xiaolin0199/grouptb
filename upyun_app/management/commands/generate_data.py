#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import optparse
import random
from django.core.management.base import BaseCommand
from ... import models

class Command(BaseCommand):
    '''
        生成假数据，用法：python manage.py generate_data --count=[记录条数]
        1. 计算所有bucket的使用总量，写入数据库
        2. 计算每个bucket的使用量，用于绘制曲线
    '''
    option_list = BaseCommand.option_list + (
        optparse.make_option('--count', default=40, help='需要生成的记录条数'),
    )
    def get_usage(self):
        total = 0
        q = models.UpYunGroupTB.objects.filter(used=True)
        for i in q:
            u = random.randint(0, 1024*1024*100)
            #print i.grouptb.group_id, u
            total += u
            models.DetailLog(log_datetime=datetime.datetime.now(),
                             upyungrouptb=i, usage=u).save()
        #print 'total:', total
        models.DailyLog(log_datetime=datetime.datetime.now(), usage=total).save()

    def handle(self, *args, **options):
        count = int(options.get('count'))
        for i in range(count):
            print i
            self.get_usage()
