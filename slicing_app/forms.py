from django import forms
from django.forms import formset_factory


class SlicingInfoForm(forms.Form):
    title = forms.CharField(label="")
    time = forms.TimeField()


class FileForm(forms.Form):
    file = forms.FileField(label="")


SlicingInfoFormset = formset_factory(SlicingInfoForm, extra=3, max_num=10, min_num=2)
