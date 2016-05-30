import datetime
from django import forms
from django.forms import DateInput
from stdb.models import Dataset


class DateInput(forms.SelectDateWidget):
    """
    creates a date widget to select the date for
    e.g. the measurement
    """
    input_type = 'date'

    def __init__(self):
        super(DateInput, self).__init__()
        past_year = datetime.date.today().year - 15
        year_field = range(int(past_year), int(datetime.date.today().year) + 3)
        self.years = year_field




class DatasetForm(forms.ModelForm):

    class Meta:
        model = Dataset
        fields = [str(i).split('.')[-1] for i in model._meta.fields]
        #cif_file = forms.FileField(label='Cif file', allow_empty_file=True, required=False)
        #res_file = forms.FileField(label='Res file', allow_empty_file=True, required=False)
        widgets = {
            'measure_date': DateInput,
            'received': DateInput,
            'output': DateInput,
        }
        fields.extend(widgets.keys())

