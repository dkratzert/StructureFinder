from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

# Create your views here.
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Dataset
from .models import Document
from .forms import DocumentForm, CifDocumentForm


def index_view(request):
    # returns all measurements of the past, not of the future
    list_of_measurements = Dataset.objects.filter(measure_date__lte=timezone.now())#[:2]
    context = {
        'latest_measurement_list': list_of_measurements
    }
    return render(request, 'data_list.html', context)


def dataset_create(request):
    """
    Creates a new Dataset
    :param request:
    :return:
    """
    form = DocumentForm(request.POST or None)
    ciffiles = CifDocumentForm(request.POST or None, request.DATA or None)
    if form.is_valid() and ciffiles.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Dataset saved successfully!")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'form': form,
        'ciffiles': ciffiles,
    }
    return render(request, "new_dataset.html", context)


def dataset_update(request, pk=None):
    """
    Updates a dataset.
    :param request:
    :param pk:
    :return:
    """
    instance = get_object_or_404(Dataset, pk=pk)
    form = DocumentForm(request.POST or None, instance=instance)
    ciffiles = CifDocumentForm(request.POST or None, request.FILES or None)
    if form.is_valid() and ciffiles.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Successfully updated!")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'dataset': instance,
        'documents': Document.objects.filter(dataname_id=pk),
        'form': form,
        'ciffiles': ciffiles,
    }
    return render(request, "new_dataset.html", context)


def delete_dataset(request, pk=None):
    instance = get_object_or_404(Dataset, pk=pk)
    instance.delete()
    messages.success(request, "Dataset deleted successfully!")
    return redirect("index")


def detail_view(request, pk=None):
    """
    returns the detailed view of all the structures.
    """
    instance = get_object_or_404(Dataset, pk=pk)
    ciffiles = CifDocumentForm(request.POST or None)#, request.DATA or None)
    context = {
        'dataset': instance,
        'documents': Document.objects.filter(dataname_id=pk),
        'ciffiles': ciffiles,
    }
    return render(request, 'detail.html', context)
















############################# old ###############
def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['cif_file'])
            newdoc.save()
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('stdb:list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load datasets and documents for the list page
    datasets = Dataset.objects.all()
    documents = Document.objects.all()
    #instance = get_object_or_404(Document, pk=?)
    context = {
        'datasets': datasets,
        'documents': documents,
        'form': form,
        #'instance': instance
    }
    # Render list page with the documents and the form
    return render(request, 'old_file_upload.html', context)
#########################################################