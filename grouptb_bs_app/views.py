# -*- coding: utf-8 -*-
from django.shortcuts import render

from grouptb_app.models import GroupTB
from grouptb_service.utils.tools import response_dict

# Create your views here.
def index(request):
    return render(request, 'grouptb_bs/index.html')

def list_current(request):
    parent_id = request.GET.get('parent_id')
    q = GroupTB.objects.all()
    if not parent_id:
        q = q.filter(parent_id__isnull=True)
    else:
        q = q.filter(parent_id=parent_id)
    q = q.values('group_id', 'name', 'parent_id').order_by('group_id')
    return response_dict(success=True, data={'records': list(q)})
