from rest_framework.permissions import BasePermission
from django.utils import timezone
import time
class IsAstronomerPermission(BasePermission):
    message = "Только астрономы могут выполнять это действие"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'astronomer') or request.user.is_superuser

class IsResearcherPermission(BasePermission):
    message = "Только исследователи могут выполнять это действие"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.userprofile.type == 'researcher' or request.user.is_superuser

class IsAdminPermission(BasePermission):
    message = "Только администраторы могут выполнять это действие"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.userprofile.type == 'admin' or request.user.is_superuser

class CanSeeStatisticsPermission(BasePermission):
    message = "У вас нет прав для просмотра статистики"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('general.can_see_statistics_page') or request.user.userprofile.can_see_statistics or request.user.is_superuser

class CanCreateObservationsPermission(BasePermission):
    message = "Недостаточно прав для создания наблюдений"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.has_perm('general.can_manage_appointments') or hasattr(request.user, 'astronomer') or request.user.is_superuser

class CanManageAstronomersPermission(BasePermission):
    message = "У вас нет прав для управления астрономами"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('general.can_manage_doctors') or request.user.is_superuser

class CanManageResearchersPermission(BasePermission):
    message = "У вас нет прав для управления исследователями"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('general.can_manage_patients') or request.user.is_superuser

class SecondFactorPermission(BasePermission):
    message = "Требуется вторая аутентификация или время действия истекло" 
    
    def has_permission(self, request, view):
        if not request.session.get('second'):
            return False

        expired_at_ts = request.session.get('second_expired_at')
        if not expired_at_ts:
            return False

        try:
            return timezone.now().timestamp() < float(expired_at_ts)
        except Exception:
            return False
    
    def _clean_session(self, request):
        """Очистка сессионных ключей"""
        keys_to_remove = ['second', 'second_expired_at']
        for key in keys_to_remove:
            if key in request.session:
                del request.session[key]
