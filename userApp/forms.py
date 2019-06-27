from django import forms
from django.utils import timezone

from .models import Orig

MONTHS = {
    1: ('一月'),
    2: ('二月'),
    3: ('三月'),
    4: ('四月'),
    5: ('五月'),
    6: ('六月'),
    7: ('七月'),
    8: ('八月'),
    9: ('九月'),
    10: ('十月'),
    11: ('十一月'),
    12: ('十二月')
}


class OrigForm(forms.Form):
    day = forms.DateField(initial=timezone.now(),
                          label='选择日期',
                          widget=forms.SelectDateWidget(months=MONTHS))
