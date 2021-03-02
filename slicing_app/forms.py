import datetime

from django import forms
from django.forms import formset_factory


class SlicingInfoForm(forms.Form):
    title = forms.CharField(label='')
    time = forms.TimeField()


class FileForm(forms.Form):
    file = forms.FileField(label='', )


SlicingInfoFormset = formset_factory(SlicingInfoForm, extra=3, max_num=10, min_num=2)
formset = SlicingInfoFormset(
    initial=[
        {'title': '1. You love me yeyeye',
         'time': datetime.time(0, 00, 00)},
        {'title': '2. Song 2',
         'time': datetime.time(0, 3, 10)},
        {'title': '3. Hey you',
         'time': datetime.time(0, 4, 00)}
    ]
)
