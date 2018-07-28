# -*- coding: utf-8 -*-
from django.contrib import admin

from . import models

# Register your models here.
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'remark')
    search_fields = ['username']

admin.site.register(models.Operator, OperatorAdmin)

class OperatorToUpYunGroupTBAdmin(admin.ModelAdmin):
    list_display = ('id', 'operator', 'upyungrouptb', 'storage_quota', 'remark')

admin.site.register(models.OperatorToUpYunGroupTB, OperatorToUpYunGroupTBAdmin)

class UpYunGroupTBAdmin(admin.ModelAdmin):
    list_display = ('id', 'grouptb', 'remark')

admin.site.register(models.UpYunGroupTB, UpYunGroupTBAdmin)
