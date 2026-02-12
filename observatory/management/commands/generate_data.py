import random
import os
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from faker import Faker

from observatory.models import Observatory, Astronomer, Researcher, Observation, SpaceObject

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])

        # Create 1000 observatories, one astronomer per observatory, and one space object per astronomer
        total = 1000
        object_types = [
            "Комета", "Астероид", "Планета", "Звезда", "Туманность", "Экзопланета"
        ]

        observatory_qs = []
        astronomer_qs = []

        for i in range(total):
            obs = Observatory.objects.create(
                name=fake.company(),
                address=fake.street_address(),
                phone=fake.phone_number()
            )
            observatory_qs.append(obs)

            # create user for astronomer
            username = f"astronomer_{i+1}"
            user = User.objects.create_user(username, fake.email(), 'astronomer123')
            user.is_staff = True
            user.save()

            astronomer = Astronomer.objects.create(
                user=user,
                name=fake.name(),
                research_field=fake.job(),
                observatory=obs
            )
            astronomer_qs.append(astronomer)

            # create one space object for this astronomer
            SpaceObject.objects.create(
                name=f"{fake.word().capitalize()}-{i+1}",
                object_type=random.choice(object_types),
                astronomer=astronomer
            )

        # Create 1000 researchers and one observation for each, linking to corresponding astronomer
        for i in range(total):
            username = f"researcher_{i+1}"
            user = User.objects.create_user(username, fake.email(), 'researcher123')
            user.save()

            researcher = Researcher.objects.create(
                user=user,
                name=fake.name(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                phone=fake.phone_number()
            )

            # create one observation linking this researcher to the astronomer with same index
            Observation.objects.create(
                astronomer=astronomer_qs[i],
                researcher=researcher,
                user=user,
                date_time=fake.date_time_between(start_date='-30d', end_date='+30d'),
                status=random.choice(['pending', 'planned', 'completed', 'cancelled'])
            )