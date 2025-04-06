import unittest
import responses
from django.test import TestCase
from django.conf import settings
from unittest.mock import patch, MagicMock

from zs.apps.courier_integrations.factories.courier_factory import CourierFactory
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError
from .mocks import MockCourierResponses
import json


class TestAramexCourierAdapter(TestCase):
    """Test ARAMEX courier adapter functionality"""
    
    def setUp(self):
        # Set up test configuration
        self.test_config = {
            'ARAMEX': {
                'api_url': 'https://api.example.com',
                'tracking_url': 'https://tracking.example.com',
                'pass_key': 'test_api_key'
            }
        }
        
        # Mock settings
        self.settings_patcher = patch('django.conf.settings.COURIER_CONFIG', self.test_config)
        self.mock_settings = self.settings_patcher.start()
        
        # Mock courier mapping
        self.mapping_patcher = patch(
            'django.conf.settings.COURIER_MAPPING', 
            {'aramex': 'zs.apps.courier_integrations.adapters.aramex.ARAMEXCourierAdapter'}
        )
        self.mock_mapping = self.mapping_patcher.start()
        
        # Get adapter instance
        self.adapter = CourierFactory.get_courier('aramex')
        
        # Set up API response mocks
        MockCourierResponses.setup_aramex_mocks()
    
    def tearDown(self):
        self.settings_patcher.stop()
        self.mapping_patcher.stop()
        responses.reset()
    
    @responses.activate
    def test_create_waybill(self):
        """Test creating a waybill with ARAMEX adapter"""
        shipment_data = {
            'reference_number': 'REF123456',
            'shipping_date': '2025-04-06',
            'customer_id': 'CUST123',
            'customer_name': 'Test Customer',
            'destination_country': 'UAE',
            'destination_city': 'Dubai',
            'postal_code': '12345',
            'phone_number': '+9715012345678',
            'address_line1': '123 Test Street',
            'package_count': 1,
            'weight': 2.5
        }
        
        result = self.adapter.create_waybill(shipment_data)
        
        # Verify result
        self.assertEqual(result['waybill_id'], 'ARAMEX12345678')
        self.assertEqual(result['status'], 'created')
        self.assertEqual(result['tracking_url'], 'https://tracking.example.com/ARAMEX12345678')
        
        # Verify request
        self.assertEqual(len(responses.calls), 1)
        request_body = json.loads(responses.calls[0].request.body)
        self.assertEqual(request_body['refNo'], 'REF123456')
        self.assertEqual(request_body['passKey'], 'test_api_key')
    
    @responses.activate
    def test_track_shipment(self):
        """Test tracking a shipment with ARAMEX adapter"""
        waybill_id = 'ARAMEX12345678'
        
        result = self.adapter.track_shipment(waybill_id)
        
        # Verify result
        self.assertEqual(result['waybill_id'], waybill_id)
        self.assertIn('current_status', result)
        self.assertEqual(len(result['history']), 2)
        
        # Verify request
        self.assertEqual(len(responses.calls), 1)
        self.assertIn('awbNo=ARAMEX12345678', responses.calls[0].request.url)
    
    @responses.activate
    def test_print_waybill_label(self):
        """Test printing a waybill label with ARAMEX adapter"""
        waybill_id = 'ARAMEX12345678'
        
        result = self.adapter.print_waybill_label(waybill_id)
        
        # Verify result is PDF content
        self.assertEqual(result, b'%PDF-1.4 mock pdf content')
        
        # Verify request
        self.assertEqual(len(responses.calls), 1)
        self.assertIn('awbNo=ARAMEX12345678', responses.calls[0].request.url)
    
    @responses.activate
    def test_cancel_shipment(self):
        """Test cancelling a shipment with ARAMEX adapter"""
        waybill_id = 'ARAMEX12345678'
        
        result = self.adapter.cancel_shipment(waybill_id)
        
        # Verify result
        self.assertEqual(result['waybill_id'], waybill_id)
        self.assertEqual(result['status'], 'cancelled')
        
        # Verify request
        self.assertEqual(len(responses.calls), 1)
        request_body = json.loads(responses.calls[0].request.body)
        self.assertEqual(request_body['awbNo'], waybill_id)
    
    def test_map_status(self):
        """Test mapping courier status to system status"""
        mappings = [
            ('shipment created', 'PENDING'),
            ('out for delivery', 'OUT_FOR_DELIVERY'),
            ('delivered', 'DELIVERED'),
        ]
        
        for courier_status, expected_status in mappings:
            mapped_status = self.adapter.map_status(courier_status)
            self.assertEqual(mapped_status, expected_status)