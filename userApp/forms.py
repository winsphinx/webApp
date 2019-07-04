from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.utils import timezone

from .models import Orig


class OrigForm(forms.ModelForm):
    class Meta:
        model = Orig
        fields = ['day']
        labels = {'day': ''}
        widgets = {
            'day':
            DatePickerInput(options={
                'format': 'YYYY-MM-DD',
                'locale': 'zh_cn',
            })
        }
