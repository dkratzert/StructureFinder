from django.core.urlresolvers import reverse
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views import generic

from stdb.models import Dataset
from .models import Document
from .forms import DocumentForm

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


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(dataname=request.FILES['docfile'])
            newdoc.save()
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )