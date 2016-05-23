from django import forms
from .models import Dataset, Document


#from .models import Document


class CifDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        ciffile = forms.FileField(label='Select a file')
        fields = [
            'cif_file',
        ]


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