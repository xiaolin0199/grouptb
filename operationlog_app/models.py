#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

# Create your models here.
class OperationLog(models.Model):
    operation_choices = ((u'新增', u'新增'), (u'修改', u'修改'), (u'删除', u'删除'))
    '''
        以下操作需要记录：
        1. 增删改upyun_app.models.Operator
        2. 增删改upyun_app.models.UpYunGroupTB
        3. 增删改upyun_app.models.OperatorToUpYunGroupTB
        为了获取执行这些操作的用户，以上记录放在middleware里
        4. 增删改grouptb_app.models.GroupTB
        以上记录放在grouptb_app.views里
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    operation = models.CharField(max_length=10, choices=operation_choices)
    model = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    log_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.description
