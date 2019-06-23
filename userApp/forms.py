from django import forms

from .models import Orig


class OrigFrom(forms.ModleFrom):
    class Meta:
        model = Orig
        fields = day
