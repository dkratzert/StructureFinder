from django.core.urlresolvers import reverse
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views import generic

from .models import Dataset
from .models import Document
from .forms import DocumentForm

class IndexView(generic.ListView):
    template_name = 'stdb/index.html'
    context_object_name = 'latest_measurement_list'

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.

        Return the last published Datasets.(not including those set to be
        published in the future)
        """
        return Dataset.objects.filter(measure_date__lte=timezone.now()).order_by('-measure_date')#[:5]


class DetailView(generic.DetailView):
    """
    returns the detailed view of all the structures.
    """
    model = Dataset
    template_name = 'stdb/detail.html'


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

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'stdb/list.html',
        {'documents': documents, 'form': form}
    )