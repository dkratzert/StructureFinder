from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'stdb/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions.(not including those set to be
        published in the future)
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]