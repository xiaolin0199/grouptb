#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from ... import models
import grouptb_app

class Command(BaseCommand):
    '''
        为UpYunGroupTB添加目前已开通的空间记录
        添加Operator
        添加OperatorToUpYunGroupTB
    '''
    def handle(self, *args, **options):
        records = [
            {'username': 'guangxi', 'password': 'oseasy0q82hb', 'ids': [450302, 450399]},
            {'username': 'hubei', 'password': 'oshueasybei', 'ids': [420398]},
            {'username': 'oseasy', 'password': 'oseasyoseasy', 'ids': [
                420102, 420602, 420106, 420682, 420111, 420103, 420105, 420699,
                420683, 420606, 422827, 422801, 420107, 610113, 610112, 421199,
            ]},
            {'username': 'shaanxi', 'password': 'oseasyp2w3tb', 'ids': [610628]},
            {'username': 'test', 'password': 'oseasy2014', 'ids': [350121]},
        ]
        for record in records:
            operator = models.Operator(username=record['username'],
                                       password=record['password'])
            operator.save()
            print 'Operator:', operator
            for bucket_id in record['ids']:
                grouptb = grouptb_app.models.GroupTB.objects.get(group_id=bucket_id)
                upyungrouptb = models.UpYunGroupTB(grouptb=grouptb)
                upyungrouptb.save()
                print 'UpYunGroupTB:', upyungrouptb
                obj = models.OperatorToUpYunGroupTB(operator=operator,
                                                    upyungrouptb=upyungrouptb)
                obj.save()
