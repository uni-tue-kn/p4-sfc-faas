"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include

from api.views import SfcViewSet, TrafficTypesViewSet, VNFViewSet
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register('SFC', SfcViewSet, 'SFC')
router.register('TrafficTypes', TrafficTypesViewSet, 'TrafficTypes')
router.register('VNF', VNFViewSet, 'VNF')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('keycloak/', include('django_keycloak.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('openapi', get_schema_view(
        title="Self-Service Portal Backend API",
        description="API for performing CRUD operations on VNF definitions, SFC definitions and TrafficType definitions",
        version="1.0.0",
        url=''
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
            template_name='swagger-ui.html',
            extra_context={'schema_url':'openapi-schema'}
        ), name='swagger-ui'),
]
