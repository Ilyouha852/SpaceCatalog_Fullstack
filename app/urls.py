"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from spacecatalog.api import AstronomerViewSet, SpaceObjectViewSet, ObjectTypeViewSet, ResearcherViewSet, ObservationViewSet, UserViewSet
from spacecatalog.views import ShowAuthorsView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register("astronomers", AstronomerViewSet, basename="astronomers")
router.register("objecttypes", ObjectTypeViewSet, basename="objecttypes")
router.register("spaceobjects", SpaceObjectViewSet, basename="spaceobjects")
router.register("researchers", ResearcherViewSet, basename="researchers")
router.register("user", UserViewSet, basename="user")
router.register("observations", ObservationViewSet, basename="observations")

urlpatterns = [
    path('', ShowAuthorsView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
