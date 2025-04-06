from django.db import models
from zs.apps.core.models import TimeStampedModel
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from zs.apps.courier_integrations.models.courier import Courier


class Shipment(TimeStampedModel):
    reference_number = models.CharField(max_length=100, unique=True)
    courier = models.ForeignKey(Courier, on_delete=models.PROTECT)
    waybill_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_tracking_update = models.DateTimeField(null=True, blank=True)
    data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.reference_number} - {self.courier.name}"
