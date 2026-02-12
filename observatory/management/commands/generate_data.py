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
        
       
        superuser = User.objects.filter(is_superuser=True).first()
        
        # Генерируем обсерватории
        observatories_data = [
            "Центральная городская обсерватория",
            "Обсерватория №1", 
            "Обсерватория №2",
            "Детская обсерватория",
            "Солнечная обсерватория",
            "Клиническая обсерватория",
            "Районная обсерватория",
            "Городская обсерватория №1",
            "Научный центр", 
            "Обсерватория исследований"
        ]
        
        for name in observatories_data:
            obs = Observatory.objects.create(
                name=name,
                address=fake.street_address(),
                phone=fake.phone_number()
            )
            # Attach a random image from media/observatories if available
            try:
                media_dir = os.path.join(str(settings.MEDIA_ROOT), 'observatories')
                files = [f for f in os.listdir(media_dir) if not f.startswith('.')]
                if files:
                    chosen = random.choice(files)
                    file_path = os.path.join(media_dir, chosen)
                    with open(file_path, 'rb') as imgf:
                        obs.picture.save(chosen, File(imgf), save=True)
            except Exception:
                pass
        
        # Генерируем астрономов
        for i in range(100):
            username = f"astronomer_{i+1}"
            user = User.objects.create_user(username, fake.email(), 'astronomer123')
            user.is_staff = True
            user.save()
            
            random_observatory = random.choice(Observatory.objects.all())
            astronomer = Astronomer.objects.create(
                user=user,
                name=f"{fake.last_name()} {fake.first_name()} {fake.middle_name()}",
                research_field=random.choice([
                    "Астрономическая физика", "Планетология", "Космология", "Радиоастрономия",
                    "Оптическая астрономия", "Инструментальная астрофизика"
                ]),
                observatory=random_observatory
            )
            # Attach a random image from media/astronomers if available
            try:
                media_dir = os.path.join(str(settings.MEDIA_ROOT), 'astronomers')
                files = [f for f in os.listdir(media_dir) if not f.startswith('.')]
                if files:
                    chosen = random.choice(files)
                    file_path = os.path.join(media_dir, chosen)
                    with open(file_path, 'rb') as imgf:
                        astronomer.picture.save(chosen, File(imgf), save=True)
            except Exception:
                pass

        for i in range(1000):
            username = f"researcher_{i+1}"
            user = User.objects.create_user(username, fake.email(), 'researcher123')
            user.save()
            
            researcher = Researcher.objects.create(
                user=user,
                name=f"{fake.last_name()} {fake.first_name()} {fake.middle_name()}",
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                phone=fake.phone_number()
            )
            # Attach a random image from media/researchers if available
            try:
                media_dir = os.path.join(str(settings.MEDIA_ROOT), 'researchers')
                files = [f for f in os.listdir(media_dir) if not f.startswith('.')]
                if files:
                    chosen = random.choice(files)
                    file_path = os.path.join(media_dir, chosen)
                    with open(file_path, 'rb') as imgf:
                        researcher.picture.save(chosen, File(imgf), save=True)
            except Exception:
                pass
            # Attach a random image from media/researchers if available
            try:
                media_dir = os.path.join(str(settings.MEDIA_ROOT), 'researchers')
                files = [f for f in os.listdir(media_dir) if not f.startswith('.')]
                if files:
                    chosen = random.choice(files)
                    file_path = os.path.join(media_dir, chosen)
                    with open(file_path, 'rb') as imgf:
                        researcher.picture.save(chosen, File(imgf), save=True)
            except Exception:
                pass

        for _ in range(1000):
            random_astronomer = random.choice(Astronomer.objects.all())
            random_researcher = random.choice(Researcher.objects.all())
            
            Observation.objects.create(
                astronomer=random_astronomer,
                researcher=random_researcher,
                user=getattr(random_researcher, 'user', None),
                date_time=fake.date_time_between(start_date='-30d', end_date='+30d'),
                status=random.choice(['pending', 'planned', 'completed', 'cancelled'])
            )

        # Create one SpaceObject per astronomer and link it
        object_types = ["Комета", "Астероид", "Планета", "Звезда", "Туманность", "Экзопланета"]
        for astronomer in Astronomer.objects.all():
            name = f"{fake.word().capitalize()}-{astronomer.id}"
            SpaceObject.objects.create(
                name=name,
                object_type=random.choice(object_types),
                astronomer=astronomer
            )