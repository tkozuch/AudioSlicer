from django import forms

class UploadFileForm(forms.Form):
    sample_text = """1- How To Fly 0:00
2- Rampampam 0:12
3- Clouds & Cream 00:22
4- Australia Street 00:32
5- These Girls 00:42"""
    title = forms.CharField(widget=forms.Textarea, label='',
                            initial=sample_text)
    file = forms.FileField(label='')