from django import forms

from .models import Orig


class OrigForm(forms.ModelForm):
    class Meta:
        model = Orig
        fields = ['day']
        labels = {'day': '选择日期'}
        widgets = {'day': forms.SelectDateWidget()}
