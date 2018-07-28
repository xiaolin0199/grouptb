# -*- coding: utf-8 -*-
from django import forms

from .models import GroupTB

class GroupTBForm(forms.ModelForm):
    class Meta:
        model = GroupTB
        # https://docs.djangoproject.com/en/1.8/releases/1.6/#modelform-without-fields-or-exclude
        # fields = '__all__'
        fields = ['group_id', 'name', 'parent']
