from django.core.management.base import BaseCommand
from django.db.models.signals import post_save, post_delete

from random import choice, randint, uniform
from datetime import datetime, timedelta

from spacecatalog.models import Astronomer, ObjectType, SpaceObject, Researcher, Observation
from spacecatalog.models import create_user_for_researcher, update_user_for_researcher, delete_user_for_researcher

from faker import Faker


fake = Faker('ru_RU')


class Command(BaseCommand):
    def handle(self, *args, **options):
        astronomers = self.generate_astronomers(count=1000)
        object_types = self.generate_object_types(count=50)
        space_objects = self.generate_space_objects(count=1000, astronomers=astronomers, object_types=object_types)
        researchers = self.generate_researchers(count=1000)
        self.generate_observations(count=1000, space_objects=space_objects, researchers=researchers)

    def generate_astronomers(self, count=1000):
        astronomers = []
        for _ in range(count):
            astronomer = Astronomer(
                name=fake.name(),
                bio=fake.text(max_nb_chars=500),
            )
            astronomers.append(astronomer)
        Astronomer.objects.bulk_create(astronomers)
        return list(Astronomer.objects.all())

    def generate_object_types(self, count=50):
        base_types = [
            ("Галактика", "Массивная гравитационно-связанная система из звёзд, межзвёздного газа, пыли и тёмной материи"),
            ("Звезда", "Массивный газовый шар, излучающий свет и тепло благодаря термоядерным реакциям"),
            ("Планета", "Небесное тело, вращающееся вокруг звезды и имеющее достаточную массу для гидростатического равновесия"),
            ("Туманность", "Облако межзвёздного газа и пыли"),
            ("Чёрная дыра", "Область пространства-времени, гравитационное притяжение которой настолько велико, что её не может покинуть даже свет"),
            ("Квазар", "Чрезвычайно яркое активное ядро галактики"),
            ("Астероид", "Небольшое небесное тело Солнечной системы"),
            ("Комета", "Небольшое небесное тело, обращающееся вокруг Солнеца по коническому сечению с весьма растянутой орбитой"),
            ("Пульсар", "Космический источник радиоизлучения"),
            ("Нейтронная звезда", "Астрономический объект, являющийся одним из конечных продуктов эволюции звёзд"),
            ("Белый карлик", "Проэволюционировавшая звезда с массой, не превышающей предел Чандрасекара"),
            ("Красный гигант", "Звезда поздних спектральных классов с высокой светимостью и протяжёнными оболочками"),
            ("Сверхновая", "Взрыв звезды, в результате которого звезда становится чрезвычайно яркой"),
            ("Планетарная туманность", "Астрономический объект, состоящий из расширяющейся светящейся оболочки"),
            ("Спутник", "Небесное тело, обращающееся вокруг планеты"),
            ("Звёздное скопление", "Гравитационно-связанная группа звёзд"),
            ("Экзопланета", "Планета, находящаяся за пределами Солнечной системы"),
            ("Сверхгигант", "Звезда с наибольшими размерами и светимостью"),
            ("Коричневый карлик", "Субзвёздный объект с массой, недостаточной для начала термоядерных реакций"),
            ("Магнетар", "Нейтронная звезда с чрезвычайно сильным магнитным полем"),
        ]

        object_types = []
        for name, description in base_types:
            object_types.append(ObjectType(name=name, description=description))

        for i in range(len(base_types), count):
            object_types.append(ObjectType(
                name=f"{fake.word().capitalize()} {choice(['объект', 'тело', 'система', 'формация'])}",
                description=fake.text(max_nb_chars=300)
            ))

        ObjectType.objects.bulk_create(object_types)
        return list(ObjectType.objects.all())

    def generate_space_objects(self, count=1000, astronomers=None, object_types=None):
        if not astronomers:
            astronomers = list(Astronomer.objects.all())
        if not object_types:
            object_types = list(ObjectType.objects.all())

        prefixes = ["NGC", "Messier", "IC", "Andromeda", "Alpha", "Beta", "Gamma", "Delta",
                    "Epsilon", "Zeta", "Eta", "Theta", "Sirius", "Vega", "Rigel", "Betelgeuse",
                    "Antares", "Aldebaran", "Spica", "Arcturus", "Capella", "Pollux", "Deneb"]

        space_objects = []
        for i in range(count):
            if i % 3 == 0:
                name = f"{choice(prefixes)}-{randint(1, 9999)}"
            elif i % 3 == 1:
                name = f"{choice(prefixes)} {fake.word().upper()}"
            else:
                name = fake.word().capitalize() + " " + choice(['I', 'II', 'III', 'IV', 'V', 'VI'])

            space_object = SpaceObject(
                name=name,
                astronomer=choice(astronomers) if astronomers and randint(1, 100) > 20 else None,
                object_type=choice(object_types) if object_types else None,
                discovery_year=randint(1600, 2024),
                description=fake.text(max_nb_chars=400),
                distance=round(uniform(0.1, 100000), 2),
                mass=round(uniform(0.001, 1000000), 3)
            )
            space_objects.append(space_object)

        SpaceObject.objects.bulk_create(space_objects)
        return list(SpaceObject.objects.all())

    def generate_researchers(self, count=1000):
        post_save.disconnect(create_user_for_researcher, sender=Researcher)
        post_save.disconnect(update_user_for_researcher, sender=Researcher)
        post_delete.disconnect(delete_user_for_researcher, sender=Researcher)

        researchers = []
        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            researcher = Researcher(
                first_name=first_name,
                last_name=last_name,
                email=fake.email(),
                card_number=f"RES-{randint(100000, 999999)}",
            )
            researchers.append(researcher)

        Researcher.objects.bulk_create(researchers)

        post_save.connect(create_user_for_researcher, sender=Researcher)
        post_save.connect(update_user_for_researcher, sender=Researcher)
        post_delete.connect(delete_user_for_researcher, sender=Researcher)

        return list(Researcher.objects.all())

    def generate_observations(self, count=1000, space_objects=None, researchers=None):
        if not space_objects:
            space_objects = list(SpaceObject.objects.all())
        if not researchers:
            researchers = list(Researcher.objects.all())

        statuses = ['planned', 'in_progress', 'completed']
        observations = []

        for _ in range(count):
            days_ago = randint(0, 1825)
            observation_date = datetime.now().date() - timedelta(days=days_ago)

            observation = Observation(
                space_object=choice(space_objects) if space_objects else None,
                status=choice(statuses),
                observation_date=observation_date,
                researcher=choice(researchers) if researchers and randint(1, 100) > 10 else None,
                notes=fake.text(max_nb_chars=500) if randint(1, 100) > 30 else None
            )
            observations.append(observation)

        Observation.objects.bulk_create(observations)