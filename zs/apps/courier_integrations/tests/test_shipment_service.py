from django.test import TestCase
from unittest.mock import patch, MagicMock

from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.tracking import ShipmentTracking
from zs.apps.courier_integrations.services.shipment_service import ShipmentService
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from .factories import CourierFactory, ShipmentFactory


class TestShipmentService(TestCase):
    """Test shipment service functionality"""
    
    def setUp(self):
        self.courier = CourierFactory(code='aramex', name='ARAMEX')
        
        # Mock courier factory
        self.factory_patcher = patch('zs.apps.courier_integrations.factories.courier_factory.CourierFactory.get_courier')
        self.mock_get_courier = self.factory_patcher.start()
        
        # Create mock adapter
        self.mock_adapter = MagicMock()
        self.mock_get_courier.return_value = self.mock_adapter
    
    def tearDown(self):
        self.factory_patcher.stop()
    
    def test_create_shipment(self):
        """Test creating a shipment"""
        # Set up mock adapter response
        self.mock_adapter.create_waybill.return_value = {
            'waybill_id': 'AWB12345678',
            'tracking_url': 'https://tracking.example.com/AWB12345678',
            'status': 'created',
            'courier_reference': 'AWB12345678',
            'raw_response': {'sawb': 'AWB12345678'}
        }
        
        # Prepare shipment data
        shipment_data = {
            'courier_code': 'aramex',
            'reference_number': 'REF123456',
            'shipping_date': '2025-04-06',
            'customer_name': 'Test Customer',
            'destination_country': 'UAE',
            'destination_city': 'Dubai',
            'postal_code': '12345',
            'phone_number': '+9715012345678',
            'address_line1': '123 Test Street',
            'package_count': 1,
            'weight': 2.5
        }
        
        # Call service method
        shipment = ShipmentService.create_shipment(shipment_data)
        
        # Verify shipment was created correctly
        self.assertEqual(shipment.reference_number, 'REF123456')
        self.assertEqual(shipment.waybill_id, 'AWB12345678')
        self.assertEqual(shipment.status, ShipmentStatus.PENDING.value)
        self.assertEqual(shipment.courier, self.courier)
        
        # Verify adapter was called correctly
        self.mock_adapter.create_waybill.assert_called_once()
    
    def test_update_tracking_status(self):
        """Test updating shipment tracking status"""
        # Create shipment
        shipment = ShipmentFactory(courier=self.courier)
        
        # Set up mock adapter response
        self.mock_adapter.track_shipment.return_value = {
            'waybill_id': shipment.waybill_id,
            'current_status': 'IN_TRANSIT',
            'current_location': 'Transit Hub',
            'timestamp': '2025-04-06T10:30:00Z',
            'history': [
                {
                    'status': 'PENDING',
                    'description': 'Shipment created',
                    'location': 'Origin',
                    'timestamp': '2025-04-05T14:20:00Z'
                },
                {
                    'status': 'IN_TRANSIT',
                    'description': 'In transit',
                    'location': 'Transit Hub',
                    'timestamp': '2025-04-06T10:30:00Z'
                }
            ],
            'raw_response': {}
        }
        
        # Call service method
        tracking_data = ShipmentService.update_tracking_status(shipment)
        
        # Verify shipment was updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, 'IN_TRANSIT')
        self.assertIsNotNone(shipment.last_tracking_update)
        
        # Verify tracking history was created
        tracking_history = ShipmentTracking.objects.filter(shipment=shipment)
        self.assertEqual(tracking_history.count(), 2)
        
        # Verify adapter was called correctly
        self.mock_adapter.track_shipment.assert_called_once_with(shipment.waybill_id)
    
    def test_cancel_shipment(self):
        """Test cancelling a shipment"""
        # Create shipment
        shipment = ShipmentFactory(courier=self.courier)
        
        # Set up mock adapter response
        self.mock_adapter.cancel_shipment.return_value = {
            'waybill_id': shipment.waybill_id,
            'status': 'cancelled',
            'message': 'Shipment cancelled successfully',
            'raw_response': {'success': True}
        }
        
        # Call service method
        result = ShipmentService.cancel_shipment(shipment)
        
        # Verify shipment was updated
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, ShipmentStatus.CANCELLED.value)
        
        # Verify adapter was called correctly
        self.mock_adapter.cancel_shipment.assert_called_once_with(shipment.waybill_id)
