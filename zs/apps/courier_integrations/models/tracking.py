from django.db import models
from zs.apps.core.models import TimeStampedModel
from zs.apps.courier_integrations.models.shipment import Shipment


class ShipmentTracking(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='tracking_history')
    courier_status = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField()
    description = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Shipment Tracking"
        verbose_name_plural = "Shipment Trackings"
        ordering = ['-timestamp']