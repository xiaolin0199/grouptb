#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import traceback
import upyun
from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    '''
        定期运行
        1. 计算所有bucket的使用总量，写入数据库
        2. 计算每个bucket的使用量，用于绘制曲线
    '''
    def get_test1_usage(self):
        username = 'oseasy'
        password = 'oseasyoseasy'
        bucket = 'oe-test1'
        up = upyun.UpYun(bucket, username, password,
                         endpoint=upyun.ED_AUTO)
        try:
            u = up.usage()
            print bucket, u
        except:
            traceback.print_exc()
        return int(u)

    def get_usage(self):
        total = 0
        q = models.OperatorToUpYunGroupTB.objects.all()
        for i in q:
            bucket = 'oebbt-%s' % i.upyungrouptb.grouptb.group_id
            up = upyun.UpYun(bucket, i.operator.username, i.operator.password,
                             endpoint=upyun.ED_AUTO)
            try:
                u = up.usage()
                print bucket, u
                total += int(u)
                obj = models.DetailLog(log_datetime=datetime.datetime.now(),
                                       upyungrouptb=i.upyungrouptb, usage=int(u))
                obj.save()
            except upyun.UpYunServiceException as e:
                err = json.loads(e.err)
                # {"msg":"bucket not exist","code":40100012,"id":"8c51b9c73d03dba73cb4b097502f2506"}
                if err['code'] == 40100012:
                    print bucket, 'not exist'
                    continue
            except:
                traceback.print_exc()
        total += self.get_test1_usage()
        print 'total:', total
        models.DailyLog(log_datetime=datetime.datetime.now(), usage=total).save()

    def handle(self, *args, **options):
        self.get_usage()
