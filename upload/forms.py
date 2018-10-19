from django import forms

class UploadFileForm(forms.Form):
    sample_text = """1- How To Fly 0:00
2- Rampampam 01:22
3- Clouds & Cream 02:22
4- Australia Street 03:17
5- These Girls 04:00"""
    title = forms.CharField(widget=forms.Textarea, label='',
                            initial=sample_text)
    file = forms.FileField(label='')