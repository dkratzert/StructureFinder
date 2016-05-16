from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.utils import timezone
from django.views import generic

from stdb.models import Dataset


class IndexView(generic.ListView):
    template_name = 'stdb/index.html'
    context_object_name = 'latest_measurement_list'

    def get_queryset(self):
        """
        Return the last five published questions.(not including those set to be
        published in the future)
        """
        return Dataset.objects.filter(measure_date__lte=timezone.now()).order_by('-measure_date')#[:5]


class DetailView(generic.DetailView):
    model = Dataset
    template_name = 'stdb/detail.html'