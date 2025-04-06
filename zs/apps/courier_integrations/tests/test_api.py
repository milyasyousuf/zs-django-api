import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from zs.apps.users.models import User
from .factories import CourierFactory, ShipmentFactory, ShipmentTrackingFactory


class TestCourierAPI(TestCase):
    """Test courier API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test user and authenticate
        
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.courier = CourierFactory(code='aramex', name='ARAMEX')
        self.shipment = ShipmentFactory(courier=self.courier)
        
        # Create tracking history
        self.tracking1 = ShipmentTrackingFactory(
            shipment=self.shipment,
            status=ShipmentStatus.PENDING.value,
            courier_status='Shipment created'
        )
        self.tracking2 = ShipmentTrackingFactory(
            shipment=self.shipment,
            status=ShipmentStatus.IN_TRANSIT.value,
            courier_status='In transit'
        )
        
        # Set up service mocks
        self.service_patcher = patch('zs.apps.courier_integrations.services.shipment_service.ShipmentService')
        self.mock_service = self.service_patcher.start()
    
    def tearDown(self):
        self.service_patcher.stop()
    
    def test_list_couriers(self):
        """Test listing available couriers"""
        url = reverse('api:courier-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'aramex')
    
    def test_list_shipments(self):
        """Test listing shipments"""
        url = reverse('api:shipment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reference_number'], self.shipment.reference_number)
    
    def test_create_shipment(self):
        """Test creating a shipment via API"""
        # Mock service response
        self.mock_service.create_shipment.return_value = self.shipment
        
        url = reverse('api:shipment-list')
        data = {
            'courier_code': 'aramex',
            'reference_number': 'REF654321',
            'customer_name': 'Test Customer',
            'shipping_date': '2025-04-06',
            'destination_country': 'UAE',
            'destination_city': 'Dubai',
            'address_line1': '123 Test Street',
            'phone_number': '+9715012345678',
            'weight': 2.5
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reference_number'], self.shipment.reference_number)
        
        # Verify service was called with correct data
        self.mock_service.create_shipment.assert_called_once()
        call_args = self.mock_service.create_shipment.call_args[0][0]
        self.assertEqual(call_args['courier_code'], 'aramex')
        self.assertEqual(call_args['reference_number'], 'REF654321')
    
    def test_track_shipment(self):
        """Test tracking a shipment via API"""
        # Mock service response
        tracking_data = {
            'waybill_id': self.shipment.waybill_id,
            'current_status': 'IN_TRANSIT',
            'current_location': 'Transit Hub',
            'timestamp': '2025-04-06T10:30:00Z',
            'history': []
        }
        self.mock_service.update_tracking_status.return_value = tracking_data
        
        url = reverse('api:shipment-track', args=[self.shipment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['waybill_id'], self.shipment.waybill_id)
        self.assertEqual(response.data['current_status'], 'IN_TRANSIT')
        
        # Verify service was called correctly
        self.mock_service.update_tracking_status.assert_called_once_with(self.shipment)
    
    def test_shipment_history(self):
        """Test getting shipment tracking history"""
        url = reverse('api:shipment-history', args=[self.shipment.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        statuses = [item['status'] for item in response.data]
        self.assertEqual(response.data[0]['status'], statuses[0])
        self.assertEqual(response.data[1]['status'], statuses[1])
    
    def test_cancel_shipment(self):
        """Test cancelling a shipment via API"""
        # Mock service response
        cancel_data = {
            'waybill_id': self.shipment.waybill_id,
            'status': 'cancelled',
            'message': 'Shipment cancelled successfully'
        }
        self.mock_service.cancel_shipment.return_value = cancel_data
        
        url = reverse('api:shipment-cancel', args=[self.shipment.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
        
        # Verify service was called correctly
        self.mock_service.cancel_shipment.assert_called_once_with(self.shipment)