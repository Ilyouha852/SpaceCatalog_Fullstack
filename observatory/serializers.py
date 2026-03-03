from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Observatory, Astronomer, Researcher, Observation, SpaceObject
from general.models import UserProfile

class ObservatorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Observatory
        fields = ['id', 'name', 'address', 'phone', 'picture']

class AstronomerSerializer(serializers.ModelSerializer):
    observatory = serializers.PrimaryKeyRelatedField(
        queryset=Observatory.objects.all(),
        required=True
    )
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        # Извлекаем поля, которые обрабатываем вручную
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', '')           # name не должен попадать в **kwargs

        if not password:
            password = 'astronomer123'

        # Генерируем уникальный username безопасно
        base = 'astronomer'
        idx = 1
        username = f"{base}_{idx}"
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base}_{idx}"

        # Создаём пользователя → сигнал сам создаст UserProfile
        try:
            user = User.objects.create_user(username=username, password=password)
        except Exception as e:
            raise serializers.ValidationError({
                'user': f'Could not create user account: {e}'
            })

        # Заполняем профиль (он уже существует благодаря сигналу)
        profile = user.userprofile
        profile.type = UserProfile.Type.astronomer
        profile.name = name
        profile.save()

        # Самое главное — создаём Astronomer
        astronomer = Astronomer.objects.create(
            user=user,
            name=name,
            **validated_data          # observatory, picture и другие поля модели
        )

        return astronomer

    def update(self, instance, validated_data):
        # name и observatory обновляем напрямую
        instance.name = validated_data.get('name', instance.name)
        instance.observatory = validated_data.get('observatory', instance.observatory)
        instance.picture = validated_data.get('picture', instance.picture)

        # Если нужно обновить пароль — отдельная логика (не через это поле)
        # if 'password' in validated_data:
        #     instance.user.set_password(validated_data['password'])
        #     instance.user.save()

        instance.save()
        return instance

    class Meta:
        model = Astronomer
        fields = ['id', 'name', 'observatory', 'picture', 'user_id', 'password']

class ResearcherSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ'])
    phone = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', None)
        birth_date = validated_data.pop('birth_date', None)
        phone = validated_data.pop('phone', None)

        if not password:
            password = 'researcher123'

        base = 'researcher'
        idx = 1
        username = f"{base}_{idx}"
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base}_{idx}"

        try:
            user = User.objects.create_user(username=username, password=password)
        except Exception as e:
            raise serializers.ValidationError({
                'user': f'Could not create user account: {e}'
            })

        if hasattr(user, 'userprofile'):
            user.userprofile.type = UserProfile.Type.researcher
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
