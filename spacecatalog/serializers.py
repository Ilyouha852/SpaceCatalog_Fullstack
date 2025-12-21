from rest_framework import serializers
from spacecatalog.models import Astronomer, SpaceObject, ObjectType, Researcher, Observation

class AstronomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Astronomer
        fields = ['id', 'name', 'bio', 'picture']

class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = ['id', 'name', 'description']

class SpaceObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceObject
        fields = ['id', 'name', 'astronomer', 'object_type', 'discovery_year', 'description', 'distance', 'mass']

class ResearcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Researcher
        fields = ['id', 'first_name', 'last_name', 'email', 'card_number', 'picture']

class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id', 'space_object', 'status', 'observation_date', 'researcher', 'notes']