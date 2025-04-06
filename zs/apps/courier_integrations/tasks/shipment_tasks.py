from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from zs.apps.courier_integrations.services.shipment_service import ShipmentService
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError

logger = logging.getLogger(__name__)

@shared_task
def update_shipment_status(shipment_id):
    """
    Update tracking status for a single shipment
    
    Args:
        shipment_id: ID of the shipment to update
    """
    try:
        shipment = Shipment.objects.get(id=shipment_id)
        
        # Skip if shipment is in a terminal state
        terminal_statuses = [
            ShipmentStatus.DELIVERED.value,
            ShipmentStatus.RETURNED.value,
            ShipmentStatus.CANCELLED.value
        ]
        
        if shipment.status in terminal_statuses:
            logger.info(f"Shipment {shipment.reference_number} is in terminal state {shipment.status}, skipping update")
            return
        
        # Update tracking status
        tracking_data = ShipmentService.update_tracking_status(shipment)
        logger.info(f"Updated tracking for shipment {shipment.reference_number}, status: {shipment.status}")
        return tracking_data
        
    except Shipment.DoesNotExist:
        logger.error(f"Shipment with ID {shipment_id} not found")
    except CourierAPIError as e:
        logger.error(f"Error updating shipment {shipment_id}: {str(e)}")


@shared_task
def update_all_active_shipments():
    """
    Update tracking for all active shipments
    
    This task should be scheduled to run periodically
    """
    # Get shipments that need tracking updates
    # Criteria:
    # 1. Not in terminal status
    # 2. Either never updated or not updated in last 6 hours
    
    terminal_statuses = [
        ShipmentStatus.DELIVERED.value,
        ShipmentStatus.RETURNED.value,
        ShipmentStatus.CANCELLED.value
    ]
    
    update_cutoff = timezone.now() - timedelta(hours=6)
    
    shipments_to_update = Shipment.objects.exclude(
        status__in=terminal_statuses
    ).filter(
        last_tracking_update__lt=update_cutoff
    )
    
    logger.info(f"Found {shipments_to_update.count()} shipments to update")
    
    for shipment in shipments_to_update:
        update_shipment_status.delay(shipment.id)