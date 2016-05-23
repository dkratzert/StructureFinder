from django import forms
from .models import Dataset, Document


#from .models import Document


class CifDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        #cif_file = forms.FileField(Document, label='Select a file')
        fields = [
            'cif_file',
        ]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Dataset
        #measure_date = forms.DateField('measure_date')
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
        ]