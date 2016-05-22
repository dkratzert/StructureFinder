from django import forms
from .models import Dataset
#from .models import Document

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = [
            'name',
            #'model.format_formula()',
            'measure_date',
            'cell_a',
            'cell_b',
            'cell_c',

        ]