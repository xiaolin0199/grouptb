#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
import upyun

# Create your models here.
class DailyLog(models.Model):
    # 每天的UpYun总使用量
    log_datetime = models.DateTimeField()
    usage = models.BigIntegerField()

class DetailLog(models.Model):
    # 每个空间的每天使用量
    log_datetime = models.DateTimeField()
    usage = models.BigIntegerField()
    upyungrouptb = models.ForeignKey('UpYunGroupTB')

class Operator(models.Model):
    '''UpYun的操作员'''
    username = models.CharField('用户名', max_length=30)
    password = models.CharField('密码', max_length=30)
    remark = models.TextField('备注', blank=True)
    upyungrouptbs = models.ManyToManyField('UpYunGroupTB',
                                           through='OperatorToUpYunGroupTB')

    class Meta:
        verbose_name = '操作员'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return u'{"username": "%s", "password": "%s", "remark": "%s"}' % (self.username, self.password, self.remark)

class OperatorToUpYunGroupTB(models.Model):
    operator = models.ForeignKey('Operator', verbose_name='操作员')
    upyungrouptb = models.ForeignKey('UpYunGroupTB', verbose_name='已开通UpYun的行政区域')
    storage_quota = models.IntegerField('空间配额', default=0)  # 空间配额（单位MB），默认为0，表示无限制
    remark = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '操作员与行政区域的对应关系'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return u'{"operator": "%s", "upyungrouptb": "%s", "storage_quota": "%d", "remark": "%s"}' % (self.operator.username, self.upyungrouptb.grouptb, self.storage_quota, self.remark)

class UpYunGroupTB(models.Model):
    '''GroupTB对应的UpYun bucket'''
    grouptb = models.OneToOneField('grouptb_app.GroupTB', verbose_name='行政区域',
                                   limit_choices_to={'group_id__lte': 999999,
                                                     'parent__isnull': False,
                                                     'parent__parent__isnull': False})
    remark = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '已开通UpYun的行政区域'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return u'{"grouptb": "%s", "remark": "%s"}' % (self.grouptb, self.remark)

    @staticmethod
    def cloud_info(grouptb):
        # 查询指定行政区域开通的所有空间-操作员记录
        # 注：空间和操作员是多对多的关系，所以一个grouptb可能有多个（空间-操作员）记录
        ret = []
        q = OperatorToUpYunGroupTB.objects.filter(upyungrouptb__grouptb=grouptb)
        for operatortoupyungrouptb in q:
            username = operatortoupyungrouptb.operator.username
            password = operatortoupyungrouptb.operator.password
            bucket = 'oebbt-%d' % grouptb.group_id
            space_used = '%s/%s' % (upyun.UpYun(bucket, username, password).usage(),
                                    operatortoupyungrouptb.storage_quota)
            ret.append({
                'provider': 'upyun', 'opened': True, 'username': username,
                'password': password, 'bucket': bucket, 'space_used': space_used,
            })
        if len(ret) == 0:
            ret.append({
                'provider': 'upyun', 'opened': False,
            })
        return ret
