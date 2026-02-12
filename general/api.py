from datetime import datetime, timedelta
import pyotp
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import time
from general.models import UserProfile


class UserProfileViewSet(GenericViewSet):
    queryset = UserProfile.objects.all()

    @action(url_path="my", methods=["GET"], detail=False)
    def get_my(self, *args, **kwargs):
        data = {
            'username': '',
            'is_authenticated': self.request.user.is_authenticated,
            'is_staff': False,
            'is_superuser': False,
            'permissions': [],
            'user_type': '',
            'can_see_statistics': False,
            'user_id': None,
            'second': False
            
        }

        if self.request.user.is_authenticated:
            data.update({
                'username': self.request.user.username,
                'is_staff': self.request.user.is_staff,
                'is_superuser': self.request.user.is_superuser,
                'permissions': list(self.request.user.get_all_permissions()),
                'user_id': self.request.user.id,
                'second': self.request.session.get('second') or False
            })

            try:
                user_profile = self.request.user.userprofile
            except:
                from general.models import UserProfile
                user_profile = UserProfile.objects.create(user=self.request.user)
            
            data.update({
                'user_type': user_profile.type,
                'can_see_statistics': user_profile.can_see_statistics,
                
            })

        return Response(data)
    @action(url_path="get-totp", methods=['GET'], detail=False)
    def get_totp(self, *args, **kwargs):

        self.request.user.userprofile.totp_key = pyotp.random_base32()
        self.request.user.userprofile.save()

        totp = pyotp.TOTP(self.request.user.userprofile.totp_key)
        url = totp.provisioning_uri(
            name=self.request.user.username,
            issuer_name="МедЦентр"
    )
    
        return Response({"url": url})

    @action(url_path="second-login", methods=['POST'], detail=False)
    def second_login(self, *args, **kwargs):
        key = self.request.user.userprofile.totp_key
        t = pyotp.TOTP(key)
        entered_key = self.request.data.get('key', '')

        # verify current code (exact match). prefer t.verify() for production/time-window.
        if entered_key == t.now():
            # use timezone-aware now and store expiry as epoch seconds in session
            expires_at = timezone.now() + timedelta(minutes=1)
            self.request.session['second'] = True
            self.request.session['second_expired_at'] = expires_at.timestamp()

            expires_in = int(self.request.session['second_expired_at'] - timezone.now().timestamp())

            return Response({
                "status": "success",
                "message": "Вторая аутентификация пройдена",
                "expires_in": expires_in
            })
        else:
            return Response({
                "status": "error",
                "message": "Неверный код"
            }, status=400)
    @action(url_path="login", methods=["POST"], detail=False)
    def process_login(self, *args, **kwargs):
        class LoginSerializer(serializers.Serializer):
            username = serializers.CharField()
            password = serializers.CharField()

        serializer = LoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
        else:
            return Response({
                "status": "failed"
            }, status=401)

        return Response({
            "status": "success"
        })
    
    @action(url_path="logout", methods=['POST'], detail=False)
    def process_logout(self, *args, **kwargs):
        logout(self.request)

        return Response({
            "status": "success"
        })
    
    