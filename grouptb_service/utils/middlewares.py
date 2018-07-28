# -*- coding: utf-8 -*-
import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete
from django.db.models.signals import pre_save
from django.http.response import HttpResponse

import operationlog_app.models
import upyun_app.models

class RevisedDjangoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.strftime('%Y-%m-%d %H:%M:%S')
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        else:
            return super(RevisedDjangoJSONEncoder, self).default(o)

class JsonResponseMiddleware(object):
    def process_response(self, request, response):
        if isinstance(response, dict):
            data = json.dumps(response, cls=RevisedDjangoJSONEncoder)
            if 'callback' in request.GET or 'callback' in request.POST:
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
            return HttpResponse(data, "application/json")
        else:
            return response

watch_instances = (
    upyun_app.models.Operator,
    upyun_app.models.OperatorToUpYunGroupTB,
    upyun_app.models.UpYunGroupTB,
)

def post_delete_cb(sender, instance, using, **kwargs):
    current_user = post_delete_cb.request.user
    if isinstance(instance, watch_instances):
        model = instance.__module__ + '.' + instance.__class__.__name__
        description = u'原始id：%s，原始值：%s' % (instance.pk, instance)
        operationlog_app.models.OperationLog(user=current_user,
                                             operation='删除',
                                             model=model,
                                             description=description).save()

def pre_save_cb(sender, instance, raw, using, update_fields, **kwargs):
    current_user = pre_save_cb.request.user
    if isinstance(instance, watch_instances):
        model = instance.__module__ + '.' + instance.__class__.__name__
        if not instance.pk:
            operation = '新增'
            description = '%s' % instance
        else:
            operation = '修改'
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            description = '原值：%s 新值：%s' % (old_instance, instance)
        operationlog_app.models.OperationLog(user=current_user,
                                             operation=operation,
                                             model=model,
                                             description=description).save()

class OperationLogMiddleware(object):
    """增删改某些model时同时记一条OperationLog"""
    def process_view(self, request, view_func, view_args, view_kwargs):
        post_delete_cb.request = request
        post_delete.connect(post_delete_cb, sender=None)
        pre_save_cb.request = request
        pre_save.connect(pre_save_cb, sender=None)

class RequireLoginMiddleware(object):
    """除了login页面，其他页面都必须登录"""
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path == reverse('admin:login') or request.user.is_authenticated():
            return None
        return login_required(view_func)(request, *view_args, **view_kwargs)
