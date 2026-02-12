from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import pyotp

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True

class UserProfile(TimestampModel):
    class Type(models.TextChoices):
        researcher = 'researcher', 'исследователь'
        astronomer = 'astronomer', 'астроном'
        admin = 'admin', 'администратор'

    name = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, blank=True, related_name='userprofile')
    type = models.TextField(choices=Type, null=True, blank=True, default=Type.researcher)
    totp_key = models.CharField(max_length=128, null=True, blank=True, default=pyotp.random_base32)

    can_see_statistics = models.BooleanField(db_default=False, null=True, blank=True)

    class Meta:
        permissions = [
            ("can_create_researchers", "Может создавать исследователей"),
            ("can_see_statistics_page", "Может видеть страницу статистики"),
            ("can_manage_astronomers", "Может управлять астрономами"),
            ("can_manage_researchers", "Может управлять исследователями"),
            ("can_manage_observations", "Может управлять наблюдениями"),
            ("can_manage_observation_records", "Может управлять записями наблюдений"),
        ]
    
    def save(self, *args, **kwargs):
        if self.id is None:
            self.totp_key = pyotp.random_base32()
       
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.type}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

