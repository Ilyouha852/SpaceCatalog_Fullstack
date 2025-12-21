from spacecatalog.models import Astronomer, SpaceObject, ObjectType, Researcher, Observation
from django.views.generic import TemplateView

class ShowAuthorsView(TemplateView):
    template_name = "authors/show_authors.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['astronomers'] = Astronomer.objects.all()
        context['objecttypes'] = ObjectType.objects.all()
        context['spaceobjects'] = SpaceObject.objects.all().prefetch_related('astronomer', 'object_type')
        context['researchers'] = Researcher.objects.all()
        context['observations'] = Observation.objects.all().select_related('space_object', 'researcher')
        return context