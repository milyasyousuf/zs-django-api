from django.db import models
from django.utils.translation import gettext_lazy as _


class ShipmentStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    PICKED_UP = "picked_up", _("Picked Up")
    IN_TRANSIT = "in_transit", _("In Transit")
    OUT_FOR_DELIVERY = "out_for_delivery", _("Out for Delivery")
    DELIVERED = "delivered", _("Delivered")
    ATTEMPTED_DELIVERY = "attempted_delivery", _("Attempted Delivery")
    FAILED = "failed", _("Failed")
    RETURNED = "returned", _("Returned")
    CANCELLED = "cancelled", _("Cancelled")
    UNKNOWN = "unknown", _("Unknown")