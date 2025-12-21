from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from spacecatalog.models import Astronomer, ObjectType, SpaceObject, Researcher, Observation
from datetime import date


class AstronomerCRUDTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.astronomer_data = {
            'name': 'Карл Янский',
            'bio': 'Американский физик и радиоинженер, основоположник радиоастрономии'
        }
        self.astronomer = Astronomer.objects.create(**self.astronomer_data)
        self.list_url = reverse('astronomers-list')
        self.detail_url = reverse('astronomers-detail', kwargs={'pk': self.astronomer.pk})

    def test_create_astronomer(self):
        new_astronomer_data = {
            'name': 'Эдвин Хаббл',
            'bio': 'Американский астроном, открывший расширение Вселенной'
        }
        response = self.client.post(self.list_url, new_astronomer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Astronomer.objects.count(), 2)
        self.assertEqual(Astronomer.objects.last().name, 'Эдвин Хаббл')

    def test_read_astronomer_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.astronomer_data['name'])
        self.assertEqual(response.data['bio'], self.astronomer_data['bio'])

    def test_update_astronomer(self):
        updated_data = {
            'name': 'Карл Янский (обновлён)',
            'bio': 'Обновлённая биография'
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.astronomer.refresh_from_db()
        self.assertEqual(self.astronomer.name, 'Карл Янский (обновлён)')

    def test_delete_astronomer(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Astronomer.objects.count(), 0)


class ObjectTypeCRUDTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.object_type_data = {
            'name': 'Галактика',
            'description': 'Массивная гравитационно-связанная система'
        }
        self.object_type = ObjectType.objects.create(**self.object_type_data)
        self.list_url = reverse('objecttypes-list')
        self.detail_url = reverse('objecttypes-detail', kwargs={'pk': self.object_type.pk})

    def test_create_object_type(self):
        new_data = {
            'name': 'Квазар',
            'description': 'Чрезвычайно яркое активное ядро галактики'
        }
        response = self.client.post(self.list_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ObjectType.objects.count(), 2)

    def test_read_object_type_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.object_type_data['name'])

    def test_update_object_type(self):
        updated_data = {
            'name': 'Галактика (обновлён)',
            'description': 'Обновлённое описание'
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.object_type.refresh_from_db()
        self.assertEqual(self.object_type.name, 'Галактика (обновлён)')

    def test_delete_object_type(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ObjectType.objects.count(), 0)


class SpaceObjectCRUDTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.astronomer = Astronomer.objects.create(
            name='Галилео Галилей',
            bio='Итальянский астроном'
        )
        self.object_type = ObjectType.objects.create(
            name='Планета',
            description='Небесное тело, вращающееся вокруг звезды'
        )
        
        self.space_object_data = {
            'name': 'Юпитер',
            'astronomer': self.astronomer.id,
            'object_type': self.object_type.id,
            'discovery_year': 1610,
            'description': 'Крупнейшая планета Солнечной системы',
            'distance': 778.5,
            'mass': 318.0
        }
        
        self.space_object = SpaceObject.objects.create(**self.space_object_data)
        
        self.list_url = reverse('spaceobjects-list')
        self.detail_url = reverse('spaceobjects-detail', kwargs={'pk': self.space_object.pk})

    def test_create_space_object(self):
        new_data = {
            'name': 'Сатурн',
            'astronomer': self.astronomer.id,
            'object_type': self.object_type.id,
            'discovery_year': 1610,
            'description': 'Планета с кольцами',
            'distance': 1427.0,
            'mass': 95.2
        }
        response = self.client.post(self.list_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SpaceObject.objects.count(), 2)

    def test_read_space_object_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.space_object_data['name'])

    def test_update_space_object(self):
        updated_data = {
            'name': 'Юпитер (обновлён)',
            'astronomer': self.astronomer.id,
            'object_type': self.object_type.id,
            'discovery_year': 1610,
            'description': 'Обновлённое описание',
            'distance': 778.5,
            'mass': 318.0
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.space_object.refresh_from_db()
        self.assertEqual(self.space_object.name, 'Юпитер (обновлён)')

    def test_delete_space_object(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SpaceObject.objects.count(), 0)


class ResearcherCRUDTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.researcher_data = {
            'first_name': 'Мария',
            'last_name': 'Кюри',
            'email': 'maria@example.com',
            'card_number': 'RES-001'
        }
        self.researcher = Researcher.objects.create(**self.researcher_data)
        self.list_url = reverse('researchers-list')
        self.detail_url = reverse('researchers-detail', kwargs={'pk': self.researcher.pk})

    def test_create_researcher(self):
        new_data = {
            'first_name': 'Альберт',
            'last_name': 'Эйнштейн',
            'email': 'albert@example.com',
            'card_number': 'RES-002'
        }
        response = self.client.post(self.list_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Researcher.objects.count(), 2)

    def test_read_researcher_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.researcher_data['first_name'])

    def test_update_researcher(self):
        updated_data = {
            'first_name': 'Мария (обновлён)',
            'last_name': 'Кюри',
            'email': 'maria.new@example.com',
            'card_number': 'RES-001'
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.researcher.refresh_from_db()
        self.assertEqual(self.researcher.first_name, 'Мария (обновлён)')

    def test_delete_researcher(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Researcher.objects.count(), 0)


class ObservationCRUDTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.astronomer = Astronomer.objects.create(
            name='Николай Коперник',
            bio='Польский астроном'
        )
        self.object_type = ObjectType.objects.create(
            name='Звезда',
            description='Массивный газовый шар'
        )
        self.space_object = SpaceObject.objects.create(
            name='Сириус',
            astronomer=self.astronomer,
            object_type=self.object_type,
            discovery_year=1844,
            description='Ярчайшая звезда ночного неба',
            distance=8.6,
            mass=2.02
        )
        
        self.researcher = Researcher.objects.create(
            first_name='Вера',
            last_name='Рубин',
            email='vera@example.com',
            card_number='RES-003'
        )
        
        self.observation_data = {
            'space_object': self.space_object.id,
            'status': 'completed',
            'observation_date': '2024-01-15',
            'researcher': self.researcher.id,
            'notes': 'Ясная ночь, отличная видимость'
        }
        
        self.observation = Observation.objects.create(**self.observation_data)
        
        self.list_url = reverse('observations-list')
        self.detail_url = reverse('observations-detail', kwargs={'pk': self.observation.pk})

    def test_create_observation(self):
        new_data = {
            'space_object': self.space_object.id,
            'status': 'in_progress',
            'observation_date': '2024-12-21',
            'researcher': self.researcher.id,
            'notes': 'Текущие наблюдения'
        }
        response = self.client.post(self.list_url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Observation.objects.count(), 2)

    def test_read_observation_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], self.observation_data['status'])

    def test_update_observation(self):
        updated_data = {
            'space_object': self.space_object.id,
            'status': 'completed',
            'observation_date': '2024-01-15',
            'researcher': self.researcher.id,
            'notes': 'Обновлённые заметки'
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.observation.refresh_from_db()
        self.assertEqual(self.observation.notes, 'Обновлённые заметки')

    def test_delete_observation(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Observation.objects.count(), 0)