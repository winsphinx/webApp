from django import forms

from .models import Orig


class OrigForm(forms.ModelForm):
    class Meta:
        model = Orig
        fields = ['day']
        labels = {'day': '选择日期'}
        day = forms.DateField(widget=forms.SelectDateWidget)
        # day = forms.DateField(widget=forms.DateInput(format='%Y%m%d'),
        #                       input_formats=('%Y%m%d', ))