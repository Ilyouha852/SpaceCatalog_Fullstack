from rest_framework import permissions
from datetime import datetime


class Has2FAVerified(permissions.BasePermission):
    
    message = "Требуется двухфакторная аутентификация для выполнения этой операции."
    
    SESSION_DURATION = 900
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        is_verified = request.session.get('second', False)
        
        if not is_verified:
            self.message = "Требуется пройти двухфакторную аутентификацию."
            return False
        
        timestamp = request.session.get('second_timestamp')
        
        if not timestamp:
            self.message = "Сессия 2FA не найдена."
            return False
        
        elapsed_time = datetime.now().timestamp() - timestamp
        
        if elapsed_time > self.SESSION_DURATION:
            request.session['second'] = False
            request.session.pop('second_timestamp', None)
            
            self.message = "Сессия 2FA истекла. Пожалуйста, пройдите аутентификацию заново."
            return False
        
        return True
