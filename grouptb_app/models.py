#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class GroupTB(models.Model):
    group_id = models.IntegerField(db_column='group_id', primary_key=True)
    name = models.CharField(max_length=30, db_index=True)
    parent = models.ForeignKey('GroupTB', to_field='group_id',
                               db_column='parent_id',
                               related_name='child_set',
                               blank=True, null=True,
                               on_delete=models.SET_NULL,
                               db_index=True)

    def __unicode__(self):
        # 350121 福建省->福州市->闽侯县
        name = self.name
        ptr = self.parent
        while ptr:
            name = ptr.name + '->' + name
            ptr = ptr.parent
        return '%s %s' % (self.group_id, name)

    class Meta:
        # 为了方便班班通系统的数据导入，这里的db_table与班班通保持一致
        # 从本系统导出数据时可以用 mysqldump -u root -p grouptb_service GroupTB > fdsfsd.sql
        # 向班班通系统导入数据时可以用 mysql -u root -p banbantong < fdsfsd.sql
        db_table = 'GroupTB'
