from django.db import models
from zs.apps.core.models import TimeStampedModel

class Courier(TimeStampedModel):
    """Courier provider configuration"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    supports_cancellation = models.BooleanField(default=False)
    config = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Courier"
        verbose_name_plural = "Couriers"
        ordering = ["name"]
    
    def __str__(self):
        return self.name