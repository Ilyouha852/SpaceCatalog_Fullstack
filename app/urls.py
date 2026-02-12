from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from general.api import UserProfileViewSet
from observatory.api import (
    ObservatoryViewSet,
    AstronomerViewSet,
    ResearcherViewSet,
    ObservationViewSet,
    SpaceObjectViewSet,
)

router = DefaultRouter()
router.register("observatories", ObservatoryViewSet, basename="observatories")
router.register("astronomers", AstronomerViewSet, basename="astronomers")
router.register("researchers", ResearcherViewSet, basename="researchers")
router.register("observations", ObservationViewSet, basename="observations")
router.register("space-objects", SpaceObjectViewSet, basename="space-objects")
router.register('users', UserProfileViewSet, basename='users')  # Добавить это

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)