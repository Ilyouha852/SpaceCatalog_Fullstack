from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_delete
import pyotp

class Astronomer(models.Model):
    name = models.TextField("ФИО")
    bio = models.TextField("Биография")
    picture = models.ImageField("Изображение", null=True, upload_to="spacecatalog_img")
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Астроном"
        verbose_name_plural = "Астрономы"

class ObjectType(models.Model):
    name = models.TextField("Название типа")
    description = models.TextField("Описание типа")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Тип объекта"
        verbose_name_plural = "Типы объектов"

class SpaceObject(models.Model):
    name = models.TextField("Название")
    astronomer = models.ForeignKey(Astronomer, on_delete=models.CASCADE, verbose_name="Открыватель", null=True, blank=True)
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE, verbose_name="Тип объекта", null=True, blank=True)
    
    discovery_year = models.IntegerField("Год открытия")
    description = models.TextField("Описание")
    distance = models.FloatField("Расстояние (световые годы)", null=True, blank=True)
    mass = models.FloatField("Масса (солнечные массы)", null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Космический объект"
        verbose_name_plural = "Космические объекты"

class Researcher(models.Model):
    first_name = models.TextField("Имя")
    last_name = models.TextField("Фамилия")
    email = models.EmailField("Email")
    card_number = models.CharField("Номер исследователя")
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, null=True)
    picture = models.ImageField("Фото", null=True, upload_to="spacecatalog_img")
    totp_key = models.CharField("TOTP ключ", max_length=128, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Исследователь"
        verbose_name_plural = "Исследователи"

class Observation(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    ]
    
    space_object = models.ForeignKey(SpaceObject, on_delete=models.CASCADE, verbose_name="Космический объект")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='planned')
    observation_date = models.DateField("Дата наблюдения", null=True, blank=True)
    researcher = models.ForeignKey(Researcher, on_delete=models.SET_NULL, verbose_name="Исследователь", null=True, blank=True)
    notes = models.TextField("Заметки", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.space_object.name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Наблюдение"
        verbose_name_plural = "Наблюдения"

@receiver(post_save, sender=Researcher)
def create_user_for_researcher(sender, instance, created, **kwargs):
    if created:
        username = f"{instance.first_name}_{instance.last_name}"
        
        try:
            user = User.objects.create_user(
                username=username,
                email=instance.email,
                password=username,
                first_name=instance.first_name,
                last_name=instance.last_name
            )
            
            instance.user = user
            instance.save()
            
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")

@receiver(post_save, sender=Researcher)
def update_user_for_researcher(sender, instance, created, **kwargs):
    if not created and instance.user:  
        try:
            instance.user.first_name = instance.first_name
            instance.user.last_name = instance.last_name
            instance.user.email = instance.email
            
            instance.user.save()
            
        except Exception as e:
            print(f"Ошибка при обновлении пользователя: {e}")

@receiver(post_delete, sender=Researcher)
def delete_user_for_researcher(sender, instance, **kwargs):
    try:
        if instance.email:
            user = User.objects.filter(email=instance.email).first()
            if user:
                user.delete()
            
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")