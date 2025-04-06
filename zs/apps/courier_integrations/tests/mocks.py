import json
import responses
from unittest.mock import patch, MagicMock
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus

class MockCourierResponses:
    """Helper class to set up mock API responses for courier tests"""
    
    @staticmethod
    def setup_aramex_mocks():
        """Set up mock responses for ARAMEX API calls"""
        # Mock create shipment response
        responses.add(
            responses.POST,
            'https://api.example.com/createShipment',
            json={
                'success': True,
                'sawb': 'ARAMEX12345678',
                'message': 'Shipment created successfully'
            },
            status=200
        )
        
        # Mock track shipment response
        responses.add(
            responses.GET,
            'https://api.example.com/getTracking',
            json={
                'success': True,
                'awbNo': 'ARAMEX12345678',
                'status': 'in transit',
                'location': 'Dubai Hub',
                'date': '2025-04-06T10:30:00Z',
                'history': [
                    {
                        'activity': 'shipment created',
                        'location': 'Shipper Warehouse',
                        'date': '2025-04-05T14:20:00Z'
                    },
                    {
                        'activity': 'in transit',
                        'location': 'Dubai Hub',
                        'date': '2025-04-06T10:30:00Z'
                    }
                ]
            },
            status=200
        )
        
        # Mock print label response
        responses.add(
            responses.GET,
            'https://api.example.com/getPDF',
            body=b'%PDF-1.4 mock pdf content',
            status=200,
            content_type='application/pdf'
        )
        
        # Mock cancel shipment response
        responses.add(
            responses.POST,
            'https://api.example.com/cancelShipment',
            json={
                'success': True,
                'message': 'Shipment cancelled successfully'
            },
            status=200
        )