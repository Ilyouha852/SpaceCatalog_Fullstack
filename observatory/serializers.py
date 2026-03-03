from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Observatory, Astronomer, Researcher, Observation, SpaceObject

class ObservatorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Observatory
        fields = ['id', 'name', 'address', 'phone', 'picture']

class AstronomerSerializer(serializers.ModelSerializer):
    observatory = serializers.PrimaryKeyRelatedField(
    queryset=Observatory.objects.all(), required=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        name = validated_data.get('name')

        if not password:
            password = 'astronomer123'

        count = Astronomer.objects.count()
        next_idx = count + 1
        username = f"astronomer_{next_idx}"

        user = User.objects.create_user(username=username, password=password)

        if hasattr(user, 'userprofile'):
            user.userprofile.type = 'astronomer'
            user.userprofile.name = name
            user.userprofile.save()

        validated_data['user'] = user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.observatory = validated_data.get('observatory', instance.observatory)
        instance.picture = validated_data.get('picture', instance.picture)

        instance.save()
        return instance

    class Meta:
        model = Astronomer
        fields = ['id', 'name', 'observatory', 'picture', 'user_id', 'password']

class ResearcherSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', None)
        birth_date = validated_data.pop('birth_date', None)
        phone = validated_data.pop('phone', None)

        if not password:
            password = 'researcher123'

        count = Researcher.objects.count()
        next_idx = count + 1
        username = f"researcher_{next_idx}"

        user = User.objects.create_user(username=username, password=password)

        if hasattr(user, 'userprofile'):
            user.userprofile.type = 'researcher'
            user.userprofile.name = name
            user.userprofile.save()

        validated_data['user'] = user

        researcher = Researcher.objects.create(
            name=name,
            birth_date=birth_date,
            phone=phone,
            **validated_data
        )
        return researcher
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.picture = validated_data.get('picture', instance.picture)
        instance.picture = validated_data.get('picture', instance.picture)

        instance.save()
        return instance

    class Meta:
        model = Researcher
        fields = ['id', 'user_id', 'name', 'birth_date', 'phone', 'picture', 'password']

class ObservationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(default=Observation.ObservationStatus.PENDING.value)
    astronomer = serializers.PrimaryKeyRelatedField(
        queryset=Astronomer.objects.all(), required=True)
    researcher = serializers.PrimaryKeyRelatedField(
        queryset=Researcher.objects.all(), required=True)

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Observation
        fields = ['id', 'date_time', 'status', 'astronomer', 'researcher', 'user']

class SpaceObjectSerializer(serializers.ModelSerializer):
    astronomer = serializers.PrimaryKeyRelatedField(
        queryset=Astronomer.objects.all(), required=True
    )
    astronomer_name = serializers.CharField(source='astronomer.name', read_only=True)

    class Meta:
        model = SpaceObject
        fields = ['id', 'name', 'object_type', 'astronomer', 'astronomer_name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
