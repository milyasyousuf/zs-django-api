import json
import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from .base import BaseCourierAdapter
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError


class ARAMEXCourierAdapter(BaseCourierAdapter):
    """ARAMEX Courier Implementation according to ARAMEX API documentation.
    
    Note: The shipping operations (create/print/cancel waybill) use the shipping
    endpoint, while tracking uses a dedicated tracking endpoint.
    """

    def create_waybill(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ARAMEX waybill"""
        # Full endpoint URL as specified in the WSDL
        endpoint = f"{self.config['api_url']}/ShippingAPI.V2/Shipping/Service_1_0.svc"

        # Format shipping date as per ARAMEX requirements
        shipping_date = datetime.datetime.strptime(
            shipment_data.get("shipping_date"), "%Y-%m-%d"
        )
        formatted_date = shipping_date.strftime("%Y-%m-%dT%H:%M:%S")

        # Create XML SOAP request payload with ClientInfo section for authentication
        # Using correct namespaces from the WSDL
        xml_payload = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Body>
            <v1:CreateShipments xmlns:v1="http://ws.aramex.net/ShippingAPI/v1/">
            <v1:ClientInfo>
                <v1:UserName>{self.config.get("username")}</v1:UserName>
                <v1:Password>{self.config.get("password")}</v1:Password>
                <v1:Version>{self.config.get("version", "v1.0")}</v1:Version>
                <v1:AccountNumber>{self.config.get("account_number")}</v1:AccountNumber>
                <v1:AccountPin>{self.config.get("account_pin")}</v1:AccountPin>
                <v1:AccountEntity>{self.config.get("account_entity")}</v1:AccountEntity>
                <v1:AccountCountryCode>{self.config.get("account_country_code")}</v1:AccountCountryCode>
            </v1:ClientInfo>
            <v1:Shipments>
                <v1:Shipment>
                <v1:Shipper>
                    <v1:Reference1>Shipper Reference</v1:Reference1>
                    <v1:AccountNumber>{self.config.get("account_number")}</v1:AccountNumber>
                    <v1:PartyAddress>
                    <v1:Line1>{self.config.get("shipper_address_line1")}</v1:Line1>
                    <v1:City>{self.config.get("shipper_city")}</v1:City>
                    <v1:CountryCode>{self.config.get("shipper_country_code")}</v1:CountryCode>
                    </v1:PartyAddress>
                    <v1:Contact>
                    <v1:PersonName>{self.config.get("shipper_name")}</v1:PersonName>
                    <v1:CompanyName>{self.config.get("shipper_company")}</v1:CompanyName>
                    <v1:PhoneNumber1>{self.config.get("shipper_phone")}</v1:PhoneNumber1>
                    <v1:EmailAddress>{self.config.get("shipper_email")}</v1:EmailAddress>
                    </v1:Contact>
                </v1:Shipper>
                <v1:Consignee>
                    <v1:Reference1>{shipment_data.get("reference_number")}</v1:Reference1>
                    <v1:PartyAddress>
                    <v1:Line1>{shipment_data.get("address_line1")}</v1:Line1>
                    <v1:City>{shipment_data.get("destination_city")}</v1:City>
                    <v1:CountryCode>{shipment_data.get("destination_country")}</v1:CountryCode>
                    </v1:PartyAddress>
                    <v1:Contact>
                    <v1:PersonName>{shipment_data.get("customer_name")}</v1:PersonName>
                    <v1:CompanyName>{shipment_data.get("customer_name")}</v1:CompanyName>
                    <v1:PhoneNumber1>{shipment_data.get("phone_number")}</v1:PhoneNumber1>
                    <v1:EmailAddress>{shipment_data.get("email", "")}</v1:EmailAddress>
                    </v1:Contact>
                </v1:Consignee>
                <v1:ShippingDateTime>{formatted_date}</v1:ShippingDateTime>
                <v1:DueDate>{shipping_date.strftime('%Y-%m-%d')}</v1:DueDate>
                <v1:Details>
                    <v1:ProductGroup>EXP</v1:ProductGroup>
                    <v1:ProductType>PD</v1:ProductType>
                    <v1:PaymentType>P</v1:PaymentType>
                    <v1:PaymentOptions>CC</v1:PaymentOptions>
                    <v1:Services>
                    <v1:Service>
                        <v1:Code>COD</v1:Code>
                        <v1:Description>Cash on Delivery</v1:Description>
                        <v1:Value>{shipment_data.get("cod_amount", 0)}</v1:Value>
                        <v1:CurrencyCode>{shipment_data.get("currency", "USD")}</v1:CurrencyCode>
                    </v1:Service>
                    </v1:Services>
                    <v1:Items>
                    <v1:ShipmentItem>
                        <v1:PackageType>Box</v1:PackageType>
                        <v1:Quantity>{shipment_data.get("package_count", 1)}</v1:Quantity>
                        <v1:Weight>
                        <v1:Unit>KG</v1:Unit>
                        <v1:Value>{shipment_data.get("weight")}</v1:Value>
                        </v1:Weight>
                    </v1:ShipmentItem>
                    </v1:Items>
                </v1:Details>
                </v1:Shipment>
            </v1:Shipments>
            </v1:CreateShipments>
        </soap:Body>
        </soap:Envelope>"""

        # Make API request with proper error handling
        response = self._make_api_request(
            "POST",
            endpoint,
            data=xml_payload,
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/CreateShipments",
            },
        )

        # Parse XML response
        root = ET.fromstring(response.content)

        # Check for API errors using XML parsing
        has_errors = self._extract_xml_value(root, ".//HasErrors")
        if has_errors and has_errors.lower() == "true":
            notifications = self._extract_xml_value(root, ".//Notifications")
            raise CourierAPIError(f"ARAMEX API error: {notifications}")

        # Extract waybill information from ProcessedShipment
        waybill_id = self._extract_xml_value(root, ".//ProcessedShipment/ID")
        label_url = self._extract_xml_value(
            root, ".//ProcessedShipment/ShipmentLabel/LabelURL"
        )

        # Transform ARAMEX response to unified format
        return {
            "waybill_id": waybill_id,
            "tracking_url": f"{self.config['tracking_url']}/{waybill_id}",
            "status": "created",
            "courier_reference": waybill_id,
            "label_url": label_url,
            "raw_response": response.text,
        }

    def print_waybill_label(self, waybill_id: str) -> Dict[str, Any]:
        """Generate ARAMEX waybill label"""
        endpoint = f"{self.config['api_url']}/ShippingAPI.V2/Shipping/Service_1_0.svc"

        xml_payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <v1:PrintLabel xmlns:v1="http://ws.aramex.net/ShippingAPI/v1/">
        <v1:ClientInfo>
            <v1:UserName>{self.config.get("username")}</v1:UserName>
            <v1:Password>{self.config.get("password")}</v1:Password>
            <v1:Version>{self.config.get("version", "v1.0")}</v1:Version>
            <v1:AccountNumber>{self.config.get("account_number")}</v1:AccountNumber>
            <v1:AccountPin>{self.config.get("account_pin")}</v1:AccountPin>
            <v1:AccountEntity>{self.config.get("account_entity")}</v1:AccountEntity>
            <v1:AccountCountryCode>{self.config.get("account_country_code")}</v1:AccountCountryCode>
        </v1:ClientInfo>
        <v1:ShipmentNumber>{waybill_id}</v1:ShipmentNumber>
        <v1:LabelInfo>
            <v1:ReportID>9201</v1:ReportID>
            <v1:ReportType>URL</v1:ReportType>
        </v1:LabelInfo>
        </v1:PrintLabel>
    </soap:Body>
    </soap:Envelope>"""

        response = self._make_api_request(
            "POST",
            endpoint,
            data=xml_payload,
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/PrintLabel",
            },
        )

        root = ET.fromstring(response.content)

        has_errors = self._extract_xml_value(root, ".//HasErrors")
        if has_errors and has_errors.lower() == "true":
            notifications = self._extract_xml_value(root, ".//Notifications")
            raise CourierAPIError(f"ARAMEX API error: {notifications}")

        label_url = self._extract_xml_value(root, ".//ShipmentLabel/LabelURL")

        return {"label_url": label_url, "raw_response": response.text}

    def track_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """Track ARAMEX shipment using the tracking API"""
        endpoint = f"{self.config['api_url']}/ShippingAPI.V2/Tracking/Service_1_0.svc"

        xml_payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <v1:TrackShipments xmlns:v1="http://ws.aramex.net/ShippingAPI/v1/">
        <v1:ClientInfo>
            <v1:UserName>{self.config.get('username')}</v1:UserName>
            <v1:Password>{self.config.get('password')}</v1:Password>
            <v1:Version>{self.config.get('version', 'v1.0')}</v1:Version>
            <v1:AccountNumber>{self.config.get('account_number')}</v1:AccountNumber>
            <v1:AccountPin>{self.config.get('account_pin')}</v1:AccountPin>
            <v1:AccountEntity>{self.config.get('account_entity')}</v1:AccountEntity>
            <v1:AccountCountryCode>{self.config.get('account_country_code')}</v1:AccountCountryCode>
        </v1:ClientInfo>
        <v1:Shipments>
            <v1:string>{waybill_id}</v1:string>
        </v1:Shipments>
        </v1:TrackShipments>
    </soap:Body>
    </soap:Envelope>"""

        response = self._make_api_request(
            "POST",
            endpoint,
            data=xml_payload,
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/TrackShipments",
            },
        )

        root = ET.fromstring(response.content)

        has_errors = self._extract_xml_value(root, ".//HasErrors")
        if has_errors and has_errors.lower() == "true":
            notifications = self._extract_xml_value(root, ".//Notifications")
            raise CourierAPIError(f"ARAMEX API error: {notifications}")

        # Assume the response contains a TrackingResult node
        current_status = self._extract_xml_value(root, ".//TrackingResult/Value")
        current_location = self._extract_xml_value(root, ".//TrackingResult/UpdateLocation")
        timestamp = self._extract_xml_value(root, ".//TrackingResult/UpdateDateTime")

        tracking_data = {
            "waybill_id": waybill_id,
            "current_status": self.map_status(current_status or ""),
            "current_location": current_location or "",
            "timestamp": timestamp or "",
            "raw_response": response.text,
        }

        return tracking_data

    def cancel_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """Cancel ARAMEX shipment"""
        endpoint = f"{self.config['api_url']}/ShippingAPI.V2/Shipping/Service_1_0.svc"

        xml_payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <v1:CancelShipments xmlns:v1="http://ws.aramex.net/ShippingAPI/v1/">
        <v1:ClientInfo>
            <v1:UserName>{self.config.get("username")}</v1:UserName>
            <v1:Password>{self.config.get("password")}</v1:Password>
            <v1:Version>{self.config.get("version", "v1.0")}</v1:Version>
            <v1:AccountNumber>{self.config.get("account_number")}</v1:AccountNumber>
            <v1:AccountPin>{self.config.get("account_pin")}</v1:AccountPin>
            <v1:AccountEntity>{self.config.get("account_entity")}</v1:AccountEntity>
            <v1:AccountCountryCode>{self.config.get("account_country_code")}</v1:AccountCountryCode>
        </v1:ClientInfo>
        <v1:ShipmentNumbers>
            <v1:string>{waybill_id}</v1:string>
        </v1:ShipmentNumbers>
        <v1:Comments>Cancellation requested by user</v1:Comments>
        </v1:CancelShipments>
    </soap:Body>
    </soap:Envelope>"""

        response = self._make_api_request(
            "POST",
            endpoint,
            data=xml_payload,
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "http://ws.aramex.net/ShippingAPI/v1/Service_1_0/CancelShipments",
            },
        )

        root = ET.fromstring(response.content)

        has_errors = self._extract_xml_value(root, ".//HasErrors")
        # if HasErrors is not "true", then consider it a success
        is_success = has_errors != "true"
        message = self._extract_xml_value(root, ".//Message") or ""

        return {
            "waybill_id": waybill_id,
            "status": "cancelled" if is_success else "cancellation_failed",
            "message": message,
            "raw_response": response.text,
        }

    def _extract_xml_value(self, root, xpath):
        """Helper method to extract values from XML using XPath."""
        try:
            # Register all namespaces in the document
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'v1': 'http://ws.aramex.net/ShippingAPI/v1/',
                's': 'http://ws.aramex.net/ShippingAPI/v2/',
            }
            
            # Clean xpath if it begins with //
            clean_xpath = xpath.lstrip('/.')
            
            # Try different namespace combinations
            for ns, uri in namespaces.items():
                # Try with namespace prefix
                try:
                    elements = root.findall(f'.//{{{uri}}}{clean_xpath}')
                    if elements and elements[0].text:
                        return elements[0].text
                except Exception:
                    pass
                    
            # If still not found, try without namespaces
            for elem in root.iter():
                if '}' in elem.tag:
                    # Remove namespace
                    elem.tag = elem.tag.split('}', 1)[1]
                    
            # Try direct search for the last part of xpath
            if '/' in clean_xpath:
                tag_name = clean_xpath.split('/')[-1]
                for elem in root.iter():
                    if elem.tag == tag_name and elem.text:
                        return elem.text
                        
        except Exception as e:
            import logging
            logging.error(f"Error extracting XML value: {e}")
            
        return None

    def _get_status_mappings(self) -> Dict[str, str]:
        """ARAMEX-specific status mappings"""
        
        return {
            "delivered": ShipmentStatus.DELIVERED.value,
            "in transit": ShipmentStatus.IN_TRANSIT.value,
            "shipment created": ShipmentStatus.PENDING.value,
            "information received": ShipmentStatus.PENDING.value,
            "out for delivery": ShipmentStatus.OUT_FOR_DELIVERY.value,
            "returned": ShipmentStatus.RETURNED.value,
            "exception": ShipmentStatus.EXCEPTION.value,
            "cancelled": ShipmentStatus.CANCELLED.value,
        }

    def _log_api_request(self, method, url, data=None, headers=None):
        """Helper method to log API requests for debugging"""
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(f"API Request: {method} {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {data}")

    def _make_api_request(self, method, url, **kwargs):
        """Override make_api_request to add detailed logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"API Request: {method} {url}")
        logger.debug(f"Headers: {kwargs.get('headers', {})}")
        
        # Don't log full XML payload in production, but do log SOAPAction
        if 'SOAPAction' in kwargs.get('headers', {}):
            logger.debug(f"SOAP Action: {kwargs['headers']['SOAPAction']}")
        
        response = super()._make_api_request(method, url, **kwargs)
        
        # Add response logging for troubleshooting
        logger.debug(f"Response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text[:500]}")  # Log first 500 chars
            
        return response