from django import forms
#from .models import Dataset, Document


#from .models import Document
from stdb.models import Dataset

"""
class CifDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        #cif_file = forms.FileField(Document, label='Select a cif file')
        fields = [
            'cif_file',
        ]

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )
"""

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Dataset
        #ciffile = forms.FileField(label='Select a cif file')
        fields = [
            'name',
            'flask_name',
            'machine',
            'measure_date',
            'formula',
            'operator',
            'cell_a',
            'cell_b',
            'cell_c',
            'alpha',
            'beta',
            'gamma',
            'cif_file',
        ]