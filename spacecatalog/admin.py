from django.contrib import admin
from .models import Astronomer, SpaceObject, ObjectType, Researcher, Observation

@admin.register(Astronomer)
class AstronomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'bio']

@admin.register(ObjectType)
class ObjectTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(SpaceObject)
class SpaceObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'astronomer', 'discovery_year', 'object_type']
    list_filter = ['object_type', 'discovery_year']

@admin.register(Researcher)
class ResearcherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'card_number']

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ['space_object', 'status', 'observation_date', 'researcher']
    list_filter = ['status', 'observation_date']