from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from .models import Observatory
from django.views.generic import TemplateView

class ShowObservatoriesView(TemplateView):
  template_name = "observatories/show_observatories.html"

  def get_context_data(self, **kwargs: any) -> dict[str, any]:
    context = super().get_context_data(**kwargs)
    context['observatories'] = Observatory.objects.all()

    return context
