from django import forms


class DocumentForm(forms.Form):
    dataname = forms.FileField(
        label='Select a file'
    )