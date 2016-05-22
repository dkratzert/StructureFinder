from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Dataset
from .models import Document
from .forms import DocumentForm


def index_view(request):
    template_name = 'stdb/index.html'
    list_of_measurements = Dataset.objects.filter(measure_date__lte=timezone.now()).order_by('-measure_date')#[:5]
    #instance = get_object_or_404(Dataset)
    context = {
        'latest_measurement_list': list_of_measurements
    }
    return render(request, template_name, context)


def detail_view(request, pk=None):
    """
    returns the detailed view of all the structures.
    """
    template_name = 'stdb/detail.html'
    instance = (Dataset.objects.all(), pk)
    context = {
                'dataset': Dataset,
                'instance': instance
    }
    return render(request, template_name, context)


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('stdb:list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load datasets and documents for the list page
    datasets = Dataset.objects.all()
    documents = Document.objects.all()
    #instance = get_object_or_404(Document, id=?)
    context = {'datasets': datasets,
               'documents': documents,
               'form': form,
               #'instance': instance
               }


    # Render list page with the documents and the form
    return render(request, 'stdb/list.html', context)