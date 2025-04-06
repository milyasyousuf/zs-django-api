from django.urls import path, include
from rest_framework.routers import DefaultRouter
from zs.apps.courier_integrations.api.v1.views import CourierViewSet, ShipmentViewSet


router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'couriers', CourierViewSet, basename='courier')

urlpatterns = [
    path('', include(router.urls)),
]