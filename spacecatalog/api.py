from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Min, Max, Q, Exists, OuterRef
from datetime import datetime, timedelta
import random
import pyotp
from spacecatalog.models import Astronomer, SpaceObject, ObjectType, Researcher, Observation
from spacecatalog.serializers import AstronomerSerializer, SpaceObjectSerializer, ObjectTypeSerializer, ResearcherSerializer, ObservationSerializer
from spacecatalog.permissions import Has2FAVerified
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .mixins import ExcelExportMixin

class AstronomerViewSet(ExcelExportMixin,
                   mixins.ListModelMixin, 
                   mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Astronomer.objects.all()
    serializer_class = AstronomerSerializer
    permission_classes = [Has2FAVerified]
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        total_count = Astronomer.objects.count()
        
        top_astronomers = Astronomer.objects.annotate(
            discoveries_count=Count('spaceobject')
        ).order_by('-discoveries_count')[:5]
        
        top_astronomers_data = [
            {
                'name': astronomer.name,
                'discoveries_count': astronomer.discoveries_count
            }
            for astronomer in top_astronomers
        ]
        
        return Response({
            'total_count': total_count,
            'top_astronomers': top_astronomers_data,
        })

class ObjectTypeViewSet(ExcelExportMixin,
                  mixins.ListModelMixin, 
                  mixins.CreateModelMixin, 
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = ObjectType.objects.all()
    serializer_class = ObjectTypeSerializer
    permission_classes = [Has2FAVerified]
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        total_count = ObjectType.objects.count()
        
        distribution = ObjectType.objects.annotate(
            objects_count=Count('spaceobject')
        ).values('name', 'objects_count').order_by('-objects_count')
        
        return Response({
            'total_count': total_count,
            'distribution': list(distribution),
        })

class SpaceObjectViewSet(ExcelExportMixin,
                 mixins.ListModelMixin, 
                 mixins.CreateModelMixin, 
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 GenericViewSet):
    queryset = SpaceObject.objects.all()
    serializer_class = SpaceObjectSerializer
    permission_classes = [Has2FAVerified]
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        stats = SpaceObject.objects.aggregate(
            total_count=Count('id'),
            avg_distance=Avg('distance'),
            avg_mass=Avg('mass'),
            min_year=Min('discovery_year'),
            max_year=Max('discovery_year'),
        )
        
        decades = {}
        if stats['min_year'] and stats['max_year']:
            for year in range((stats['min_year'] // 10) * 10, ((stats['max_year'] // 10) + 1) * 10, 10):
                decade_end = year + 9
                count = SpaceObject.objects.filter(
                    discovery_year__gte=year,
                    discovery_year__lte=decade_end
                ).count()
                if count > 0:
                    decades[f"{year}-{decade_end}"] = count
        
        return Response({
            'total_count': stats['total_count'],
            'avg_distance': round(stats['avg_distance'], 2) if stats['avg_distance'] else None,
            'avg_mass': round(stats['avg_mass'], 2) if stats['avg_mass'] else None,
            'discovery_year_range': {
                'min': stats['min_year'],
                'max': stats['max_year'],
            },
            'by_decade': decades,
        })

class UserViewSet(viewsets.GenericViewSet):

    @action(detail=False, url_path="info", methods=["GET"])
    def get_info(self, request, *args, **kwargs):
        return Response({
            "username": request.user.username,
            "is_authenticated": request.user.is_authenticated,
           
            "is_staff": request.user.is_staff,
        })

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request, *args, **kwargs):
        username = self.request.data['username']
        password = self.request.data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            return Response({
                'success': True,
            })

        return Response({
            'success': False,
        })
    @action(detail=False, url_path="logout", methods=["POST"])
    def logout_user(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, url_path="get_totp", methods=["GET"])
    def get_totp(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Необходима аутентификация'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            researcher = Researcher.objects.get(user=request.user)
            researcher.totp_key = pyotp.random_base32()
            researcher.save()
            
            url = pyotp.totp.TOTP(researcher.totp_key).provisioning_uri(
                name=request.user.username, issuer_name="SpaceCatalog"
            )
            
            return Response({
                'success': True,
                'url': url
            })
        except Researcher.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Профиль исследователя не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, url_path="verify_2fa", methods=["POST"])
    def verify_2fa(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Необходима аутентификация'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        pin = request.data.get('pin')
        
        if not pin:
            return Response({
                'success': False,
                'error': 'Код не предоставлен'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            researcher = Researcher.objects.get(user=request.user)
            
            if not researcher.totp_key:
                return Response({
                    'success': False,
                    'error': 'TOTP ключ не настроен. Сначала запросите ключ.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            t = pyotp.totp.TOTP(researcher.totp_key)
            
            if pin == t.now():
                request.session['second'] = True
                request.session['second_timestamp'] = datetime.now().timestamp()
                
                return Response({
                    'success': True,
                    'message': 'Двухфакторная аутентификация успешна',
                    'expires_in': 900
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Неверный код'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Researcher.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Профиль исследователя не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, url_path="check_2fa_status", methods=["GET"])
    def check_2fa_status(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'is_verified': False,
                'authenticated': False
            })
        
        is_verified = request.session.get('second', False)
        timestamp = request.session.get('second_timestamp')
        
        if not is_verified or not timestamp:
            return Response({
                'is_verified': False,
                'authenticated': True
            })
        
        elapsed_time = datetime.now().timestamp() - timestamp
        remaining_time = max(0, 900 - int(elapsed_time))
        
        if remaining_time == 0:
            request.session['second'] = False
            request.session.pop('second_timestamp', None)
            
            return Response({
                'is_verified': False,
                'authenticated': True,
                'expired': True
            })
        
        return Response({
            'is_verified': True,
            'authenticated': True,
            'remaining_seconds': remaining_time,
            'remaining_minutes': remaining_time // 60
        })
class ResearcherViewSet(ExcelExportMixin,
                   mixins.ListModelMixin, 
                   mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Researcher.objects.all()
    serializer_class = ResearcherSerializer
    permission_classes = [Has2FAVerified]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'id']
    search_fields = ['first_name', 'last_name', 'email']
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            return qs
        
        if self.request.user.is_authenticated:
            return qs.filter(user=self.request.user)
        
        return Researcher.objects.none()
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        total_count = Researcher.objects.count()
        
        active_count = Researcher.objects.annotate(
            observations_count=Count('observation')
        ).filter(observations_count__gt=0).count()
        
        top_researchers = Researcher.objects.annotate(
            observations_count=Count('observation')
        ).order_by('-observations_count')[:5]
        
        top_researchers_data = [
            {
                'name': f"{researcher.first_name} {researcher.last_name}",
                'observations_count': researcher.observations_count
            }
            for researcher in top_researchers if researcher.observations_count > 0
        ]
        
        return Response({
            'total_count': total_count,
            'active_count': active_count,
            'top_researchers': top_researchers_data,
        })

class ObservationViewSet(ExcelExportMixin,
                         mixins.ListModelMixin, 
                         mixins.CreateModelMixin, 
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    permission_classes = [Has2FAVerified]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['researcher', 'status']
    ordering_fields = ['observation_date']

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            return qs
        
        if self.request.user.is_authenticated:
            try:
                researcher = Researcher.objects.get(user=self.request.user)
                return qs.filter(researcher=researcher)
            except Researcher.DoesNotExist:
                return Observation.objects.none()
        
        return Observation.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            try:
                researcher = Researcher.objects.get(user=self.request.user)
                serializer.save(researcher=researcher)
            except Researcher.DoesNotExist:
                serializer.save()
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        total_count = Observation.objects.count()
        
        by_status = Observation.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        status_distribution = {item['status']: item['count'] for item in by_status}
        
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_count = Observation.objects.filter(
            observation_date__gte=thirty_days_ago
        ).count()
        
        seven_days_ago = datetime.now().date() - timedelta(days=7)
        last_week_count = Observation.objects.filter(
            observation_date__gte=seven_days_ago
        ).count()
        
        return Response({
            'total_count': total_count,
            'by_status': {
                'planned': status_distribution.get('planned', 0),
                'in_progress': status_distribution.get('in_progress', 0),
                'completed': status_distribution.get('completed', 0),
            },
            'recent_observations': {
                'last_7_days': last_week_count,
                'last_30_days': recent_count,
            },
        })