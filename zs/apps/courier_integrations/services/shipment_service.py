from typing import Dict, Any
from django.utils import timezone
from django.db import transaction
from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.tracking import ShipmentTracking
from zs.apps.courier_integrations.factories.courier_factory import CourierFactory
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError
from datetime import date, datetime

class ShipmentService:
    """Business logic for shipment operations"""
    
    @staticmethod
    @transaction.atomic
    def create_shipment(data: Dict[str, Any]) -> Shipment:
        """
        Create a new shipment with waybill from courier
        
        Args:
            data: Shipment data including courier_code
            
        Returns:
            Created Shipment instance
            
        Raises:
            ValidationError: If courier is invalid or inactive
            CourierAPIError: If courier API returns an error
        """

        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                data[key] = value.isoformat()

        courier_code = data.pop('courier_code')
        courier = Courier.objects.get(code=courier_code, is_active=True)
        
        # Create shipment record first without waybill
        shipment = Shipment.objects.create(
            reference_number=data['reference_number'],
            courier=courier,
            status=ShipmentStatus.PENDING.value,
            data=data
        )
        
        # Get courier adapter and create waybill
        courier_adapter = CourierFactory.get_courier(courier_code)
        result = courier_adapter.create_waybill(data)
        
        # Update shipment with waybill information
        shipment.waybill_id = result['waybill_id']
        shipment.save()
        
        return shipment
    
    @staticmethod
    def update_tracking_status(shipment: Shipment) -> Dict[str, Any]:
        """
        Update shipment tracking status
        
        Args:
            shipment: Shipment instance to update
            
        Returns:
            Tracking data dictionary
            
        Raises:
            CourierAPIError: If courier API returns an error
        """
        courier_adapter = CourierFactory.get_courier(shipment.courier.code)
        tracking_data = courier_adapter.track_shipment(shipment.waybill_id)
        
        with transaction.atomic():
            # Update shipment status
            shipment.status = tracking_data['current_status']
            shipment.last_tracking_update = timezone.now()
            shipment.save()
            
            # Create tracking history records
            for event in tracking_data.get('history', []):
                ShipmentTracking.objects.create(
                    shipment=shipment,
                    courier_status=event.get('description', ''),
                    status=event.get('status', ''),
                    location=event.get('location', ''),
                    timestamp=event.get('timestamp', timezone.now()),
                    description=event.get('description', ''),
                    raw_data=event
                )
        
        return tracking_data
    
    @staticmethod
    def cancel_shipment(shipment: Shipment) -> Dict[str, Any]:
        """
        Cancel a shipment
        
        Args:
            shipment: Shipment to cancel
            
        Returns:
            Cancellation result
            
        Raises:
            CourierNotImplementedError: If courier doesn't support cancellation
            CourierAPIError: If courier API returns an error
        """
        courier_adapter = CourierFactory.get_courier(shipment.courier.code)
        result = courier_adapter.cancel_shipment(shipment.waybill_id)
        
        # Update shipment status if cancelled
        if result.get('status') == 'cancelled':
            with transaction.atomic():
                shipment.status = ShipmentStatus.CANCELLED.value
                shipment.save()
        
        return result