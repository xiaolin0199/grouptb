# -*- coding: utf-8 -*-
from django.contrib import admin

from . import models

# Register your models here.
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'operation', 'model', 'description', 'log_datetime')

admin.site.register(models.OperationLog, OperationLogAdmin)
