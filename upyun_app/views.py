#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render

from . import models
import grouptb_app.models
from grouptb_service.utils.tools import response_dict

# Create your views here.
def index(request):
    return render(request, 'upyun_bs/index.html')

def dailylog(request):
    q = models.DailyLog.objects.all().values().order_by('-log_datetime')
    return response_dict(success=True, data={'records': list(q)})

def detaillog(request):
    group_id = request.GET.get('group_id')
    try:
        g = models.UpYunGroupTB.objects.get(grouptb__group_id=int(group_id))
        q = models.DetailLog.objects.filter(upyungrouptb=g)
        q = q.values('log_datetime', 'usage').order_by('-log_datetime')
        ret = response_dict(success=True, records=list(q))
    except models.UpYunGroupTB.DoesNotExist:
        ret = response_dict(success=False, msg='错误的id')
    return ret

def districts_usage(request):
    """最近一天的各区县使用量，按GB从大到小排序

    {
        "log_datetime": "2016-06-29",
        "usage": [
            {
                "upyungrouptb__grouptb__group_id": 422801,
                "upyungrouptb__grouptb__name": "恩施市",
                "upyungrouptb__grouptb__parent__name": "恩施土家族苗族自治州",
                "upyungrouptb__grouptb__parent__parent__name": "湖北省",
                "usage": 215342560115
            },
        ]
    }

    """
    log_datetime = models.DetailLog.objects.latest('log_datetime').log_datetime
    q = models.DetailLog.objects.filter(
        log_datetime__year=log_datetime.year,
        log_datetime__month=log_datetime.month,
        log_datetime__day=log_datetime.day
    ).order_by('-usage')
    q = q.values('usage', 'upyungrouptb__grouptb__group_id',
                 'upyungrouptb__grouptb__name',
                 'upyungrouptb__grouptb__parent__name',
                 'upyungrouptb__grouptb__parent__parent__name')
    return JsonResponse({'log_datetime': log_datetime.date(), 'usage': list(q)})

def group(request):
    q = models.UpYunGroupTB.objects.all()
    q = q.values('grouptb__group_id', 'grouptb__name')
    q = q.order_by('grouptb__group_id')
    return response_dict(success=True, records=list(q))

def group_tree(request):
    '''
    已开通upyun的group树形
    {
        420000: {
            name: 湖北省, children: {
                420100: {
                    name: 武汉市, children: {
                        420102: {name: 江岸区}, 420106: {name: 武昌区},
                    }
                }
            }
        }
    }
    '''
    q = grouptb_app.models.GroupTB.objects.filter(upyungrouptb__isnull=False)
    tree = {}
    for country in q:
        province = country.parent.parent
        city = country.parent
        if province.group_id not in tree:
            tree[province.group_id] = {'name': province.name, 'children': {}}
        if city.group_id not in tree[province.group_id]['children']:
            tree[province.group_id]['children'][city.group_id] = {'name': city.name, 'children': {}}
        tree[province.group_id]['children'][city.group_id]['children'][country.group_id] = {'name': country.name}
    return response_dict(success=True, data={'tree': tree})
