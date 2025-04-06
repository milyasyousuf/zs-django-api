from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "api"

urlpatterns = [
    path("v1/", include("zs.apps.courier_integrations.api.v1.urls")),
] + router.urls