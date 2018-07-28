# -*- coding: utf-8 -*-
from django import forms
from .models import Operator

class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        exclude = ['id']
