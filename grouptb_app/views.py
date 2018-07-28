# -*- coding: utf-8 -*-
from django.shortcuts import render

from .forms import GroupTBForm
from .models import GroupTB
from grouptb_service.utils.tools import response_dict
import operationlog_app.models
import upyun_app.models

# Create your views here.
def index(request):
    return render(request, 'grouptb/index.html')

def add(request):
    if request.method == 'POST':
        form = GroupTBForm(request.POST)
        if form.is_valid():
            instance = form.save()
            operationlog_app.models.OperationLog(user=request.user,
                                                 operation='新增',
                                                 model=instance.__module__ + '.' + instance.__class__.__name__,
                                                 description='%s' % instance).save()
            return response_dict(success=True, msg='添加成功')
        else:
            return response_dict(success=False, msg='添加失败',
                                 errors=form.errors)

def cloud_info(request):
    group_id = request.GET.get('group_id')
    records = [
        {'provider': 'qiniu', 'opened': False, 'username': '', 'bucket': '', 'space_used': 0}
    ]
    try:
        grouptb = GroupTB.objects.get(group_id=group_id)
    except GroupTB.DoesNotExist:
        return response_dict(success=False, msg='错误的group_id')
    upyun_info = upyun_app.models.UpYunGroupTB.cloud_info(grouptb)
    records.extend(upyun_info)
    return response_dict(success=True, data={'records': records})

def delete(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        try:
            instance = GroupTB.objects.get(group_id=group_id)
            if instance.child_set.count() > 0:
                return response_dict(success=False, msg='该记录还有下属的子节点，无法删除')
        except GroupTB.DoesNotExist:
            return response_dict(success=False, msg='错误的group_id')
        model = instance.__module__ + '.' + instance.__class__.__name__
        description = u'原始id：%s，原始值：%s' % (instance.pk, instance)
        operationlog_app.models.OperationLog(user=request.user,
                                             operation='删除',
                                             model=model,
                                             description=description).save()
        instance.delete()
        return response_dict(success=True, msg='删除成功')

def edit(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        try:
            old_instance = GroupTB.objects.get(group_id=group_id)
        except GroupTB.DoesNotExist:
            return response_dict(success=False, msg='错误的group_id')
        form = GroupTBForm(request.POST, instance=old_instance)
        if form.is_valid():
            new_instance = form.save()
            model = new_instance.__module__ + '.' + new_instance.__class__.__name__
            description = '原值：%s 新值：%s' % (old_instance, new_instance)
            operationlog_app.models.OperationLog(user=request.user,
                                                 operation='修改',
                                                 model=model,
                                                 description=description).save()
            return response_dict(success=True, msg='编辑成功')
        else:
            return response_dict(success=False, msg='编辑失败',
                                 errors=form.errors)

def list_current(request):
    parent_id = request.GET.get('parent_id')
    q = GroupTB.objects.all()
    if not parent_id:
        q = q.filter(parent_id__isnull=True)
    else:
        q = q.filter(parent_id=parent_id)
    q = q.values('group_id', 'name', 'parent_id').order_by('group_id')
    return response_dict(success=True, data={'records': list(q)})
