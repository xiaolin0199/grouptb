#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import traceback
from django.core.management.base import BaseCommand
from ... import models

class Command(BaseCommand):
    '''
        从upyun_usage数据库载入DailyLog和DetailLog
    '''
    def daily(self, cursor):
        sql = """SELECT db_dailylog.log_datetime, db_dailylog.usage FROM db_dailylog"""
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            obj = models.DailyLog(log_datetime=row[0], usage=row[1])
            obj.save()
            print obj

    def detail(self, cursor):
        sql = """SELECT db_detaillog.log_datetime, db_detaillog.usage, group_id FROM db_detaillog"""
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            try:
                upyungrouptb = models.UpYunGroupTB.objects.get(grouptb__group_id=row[2])
            except models.UpYunGroupTB.DoesNotExist:
                print row
                continue
            obj = models.DetailLog(log_datetime=row[0], usage=row[1], upyungrouptb=upyungrouptb)
            obj.save()
            print obj

    def handle(self, *args, **options):
        try:
            conn = MySQLdb.connect(host='127.0.0.1', port=3306,
                                   user='root', passwd='oseasy',
                                   db='upyun_usage', charset='utf8')
            cursor = conn.cursor()
        except:
            traceback.print_exc()
            return
        self.daily(cursor)
        print '-' * 40
        self.detail(cursor)
