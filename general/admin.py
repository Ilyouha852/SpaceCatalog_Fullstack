from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'name', 'birthday', 'can_see_statistics')
    list_filter = ('type', 'can_see_statistics')
    search_fields = ('user__username', 'name','totp_key')
    fields = ('user', 'name', 'birthday', 'type', 'can_see_statistics', 'totp_key')