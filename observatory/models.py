from django.db import models
from django.contrib.auth.models import User
from general.models import TimestampModel

class Observatory(models.Model):
    name = models.TextField("Название")
    phone = models.TextField("Телефон")
    picture = models.ImageField("Изображение", null=True, upload_to="observatories")
    address = models.TextField("Адрес", null=True, blank=True)
    class Meta:
        verbose_name = "Обсерватория"
        verbose_name_plural = "Обсерватории"

    def __str__(self) -> str:
        return self.name

class Astronomer(models.Model):
    name = models.TextField("Имя")
    research_field = models.TextField("Область исследований")
    observatory = models.ForeignKey("Observatory", on_delete=models.CASCADE, null=True)
    picture = models.ImageField("Изображение", null=True, upload_to="astronomers")
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, null=True, blank=True, related_name='astronomer')
    class Meta:
        verbose_name = "Астроном"
        verbose_name_plural = "Астрономы"

    def __str__(self) -> str:
        return self.name

class Researcher(TimestampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='researcher')
    
    name = models.CharField("Имя", max_length=150, null=True, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    phone = models.CharField("Телефон", max_length=20, null=True, blank=True)
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="researchers")
    picture = models.ImageField("Изображение", null=True, blank=True, upload_to="researchers")

    class Meta:
        verbose_name = "Исследователь"
        verbose_name_plural = "Исследователи"

    def __str__(self) -> str:
        return self.user.username if self.user else "Без пользователя"
      
    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

class Observation(models.Model):
    class ObservationStatus(models.TextChoices):
        PENDING = 'pending'
        PLANNED = 'planned'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'

    date_time = models.DateTimeField("Дата и время")
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=ObservationStatus.choices,
        default=ObservationStatus.PENDING
    )

    astronomer = models.ForeignKey("Astronomer", on_delete=models.CASCADE, null=True)
    researcher = models.ForeignKey("Researcher", on_delete=models.CASCADE, null=True)
    
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Наблюдение"
        verbose_name_plural = "Наблюдения"

    def __str__(self) -> str:
        return f"Наблюдение {self.id} - {self.date_time}"
    
class SpaceObject(models.Model):
    name = models.CharField("Имя", max_length=200)
    object_type = models.CharField("Тип объекта", max_length=100)
    astronomer = models.OneToOneField("Astronomer", on_delete=models.CASCADE, related_name='space_object')

    class Meta:
        verbose_name = "Космический объект"
        verbose_name_plural = "Космические объекты"

    def __str__(self) -> str:
        return f"{self.name} ({self.object_type})"
