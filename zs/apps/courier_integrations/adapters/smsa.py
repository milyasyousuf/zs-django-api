import json
from typing import Dict, Any, Optional
from .base import BaseCourierAdapter

class SMSACourierAdapter(BaseCourierAdapter):
    """SMSA Courier Implementation"""
    
    def create_waybill(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create SMSA waybill"""
        endpoint = f"{self.config['api_url']}/createShipment"
        
        # Transform system data to SMSA format
        smsa_payload = {
            "passKey": self.config['pass_key'],
            "refNo": shipment_data['reference_number'],
            "sentDate": shipment_data['shipping_date'],
            "idNo": shipment_data['customer_id'],
            "cName": shipment_data['customer_name'],
            "cntry": shipment_data['destination_country'],
            "cCity": shipment_data['destination_city'],
            "cZip": shipment_data['postal_code'],
            "cPOBox": shipment_data.get('po_box', ''),
            "cMobile": shipment_data['phone_number'],
            "cTel1": shipment_data.get('alternative_phone', ''),
            "cAddr1": shipment_data['address_line1'],
            "cAddr2": shipment_data.get('address_line2', ''),
            "shipType": "DLV",
            "PCs": shipment_data['package_count'],
            "cEmail": shipment_data.get('email', ''),
            "weight": shipment_data['weight'],
            "itemDesc": shipment_data.get('description', 'Package'),
        }
        
        response = self.session.post(
            endpoint,
            json=smsa_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"SMSA API error: {response.text}")
            
        result = response.json()
        
        # Transform SMSA response to unified format
        return {
            "waybill_id": result.get("sawb", ""),
            "tracking_url": f"{self.config['tracking_url']}/{result.get('sawb', '')}",
            "status": "created",
            "courier_reference": result.get("sawb", ""),
            "raw_response": result
        }
    
    def print_waybill_label(self, waybill_id: str) -> bytes:
        """Generate SMSA waybill label"""
        endpoint = f"{self.config['api_url']}/getPDF"
        
        params = {
            "awbNo": waybill_id,
            "passKey": self.config['pass_key']
        }
        
        response = self.session.get(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(f"SMSA API error: {response.text}")
            
        return response.content
    
    def track_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """Track SMSA shipment"""
        endpoint = f"{self.config['api_url']}/getTracking"
        
        params = {
            "awbNo": waybill_id,
            "passkey": self.config['pass_key']
        }
        
        response = self.session.get(endpoint, params=params)
        
        if response.status_code != 200:
            raise Exception(f"SMSA API error: {response.text}")
            
        result = response.json()
        
        # Transform SMSA tracking response to unified format
        tracking_data = {
            "waybill_id": waybill_id,
            "current_status": self.map_status(result.get("status", "")),
            "current_location": result.get("location", ""),
            "timestamp": result.get("date", ""),
            "history": [
                {
                    "status": self.map_status(event.get("activity", "")),
                    "description": event.get("activity", ""),
                    "location": event.get("location", ""),
                    "timestamp": event.get("date", "")
                }
                for event in result.get("history", [])
            ],
            "raw_response": result
        }
        
        return tracking_data
    
    def _get_status_mappings(self) -> Dict[str, str]:
        """SMSA-specific status mappings"""
        return {
            "shipment created": "PENDING",
            "out for delivery": "OUT_FOR_DELIVERY",
            "shipment picked up": "PICKED_UP",
            "delivered": "DELIVERED",
            "delivery failed": "FAILED",
            "returned to shipper": "RETURNED"
        }
    
    def cancel_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """Cancel SMSA shipment"""
        endpoint = f"{self.config['api_url']}/cancelShipment"
        
        payload = {
            "awbNo": waybill_id,
            "passKey": self.config['pass_key'],
            "reason": "Customer request"
        }
        
        response = self.session.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"SMSA API error: {response.text}")
            
        result = response.json()
        
        return {
            "waybill_id": waybill_id,
            "status": "cancelled" if result.get("success", False) else "cancellation_failed",
            "message": result.get("message", ""),
            "raw_response": result
        }