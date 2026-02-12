from django.test import TestCase
from django.test import TestCase
from observatory.models import Observatory, Astronomer, Researcher, Observation


class TestObservatoryModels(TestCase):
    def test_observatory_crud(self):
        # CREATE
        obs = Observatory.objects.create(name='Обсерватория №1', address='ул. Ленина, 1', phone='+7 (3952) 111-111')
        self.assertIsNotNone(obs.id)

        # READ
        self.assertEqual(Observatory.objects.count(), 1)
        got = Observatory.objects.get(id=obs.id)
        self.assertEqual(got.name, 'Обсерватория №1')

        # UPDATE
        obs.name = 'Обсерватория №1 Обновленная'
        obs.save()
        self.assertEqual(Observatory.objects.get(id=obs.id).name, 'Обсерватория №1 Обновленная')

        # DELETE
        obs.delete()
        self.assertEqual(Observatory.objects.count(), 0)


class TestAstronomerModels(TestCase):
    def test_astronomer_crud(self):
        obs = Observatory.objects.create(name='Obs', phone='123')
        astro = Astronomer.objects.create(name='Иванов', research_field='Астрономия', observatory=obs)
        self.assertIsNotNone(astro.id)

        self.assertEqual(Astronomer.objects.count(), 1)
        got = Astronomer.objects.get(id=astro.id)
        self.assertEqual(got.name, 'Иванов')

        got.name = 'Петров'
        got.save()
        self.assertEqual(Astronomer.objects.get(id=astro.id).name, 'Петров')

        got.delete()
        self.assertEqual(Astronomer.objects.count(), 0)


class TestResearcherModels(TestCase):
    def test_researcher_crud(self):
        r = Researcher.objects.create(name='Сидоров', birth_date='1990-01-01', phone='+7')
        self.assertIsNotNone(r.id)

        self.assertEqual(Researcher.objects.count(), 1)
        got = Researcher.objects.get(id=r.id)
        self.assertEqual(got.name, 'Сидоров')

        got.phone = '+7-222'
        got.save()
        self.assertEqual(Researcher.objects.get(id=r.id).phone, '+7-222')

        got.delete()
        self.assertEqual(Researcher.objects.count(), 0)


class TestObservationModels(TestCase):
    def test_observation_crud(self):
        obs = Observatory.objects.create(name='Obs', phone='123')
        astro = Astronomer.objects.create(name='A', research_field='F', observatory=obs)
        researcher = Researcher.objects.create(name='R')

        o = Observation.objects.create(astronomer=astro, researcher=researcher, date_time='2025-01-15T10:00:00Z', status='planned')
        self.assertIsNotNone(o.id)

        self.assertEqual(Observation.objects.count(), 1)
        o.status = 'completed'
        o.save()
        self.assertEqual(Observation.objects.get(id=o.id).status, 'completed')

        o.delete()
        self.assertEqual(Observation.objects.count(), 0)
