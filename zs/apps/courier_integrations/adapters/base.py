# courier_integration/adapters/base.py
import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError
from zs.apps.courier_integrations.interfaces.courier_interface import CourierInterface


logger = logging.getLogger(__name__)


class BaseCourierAdapter(CourierInterface):
    """Base implementation for courier adapters"""
    
    def __init__(self):
        """Initialize adapter with HTTP session and config"""
        self.session = self._create_retry_session()
        self.config = self._load_config()
    
    def _create_retry_session(self, 
                             retries=3, 
                             backoff_factor=0.3,
                             status_forcelist=(500, 502, 504)):
        """Create session with retry mechanism"""
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _load_config(self) -> Dict[str, Any]:
        """Load courier-specific configuration"""
        from django.conf import settings
        courier_name = self.__class__.__name__.replace('CourierAdapter', '')
        return settings.COURIER_CONFIG.get(courier_name, {})
    
    def map_status(self, courier_status: str) -> str:
        """
        Map courier-specific status to unified system status
        """
        status_mapping = {
            # Common status mappings across all couriers
            "delivered": ShipmentStatus.DELIVERED.value,
            "in_transit": ShipmentStatus.IN_TRANSIT.value,
            "pending": ShipmentStatus.PENDING.value,
            "returned": ShipmentStatus.RETURNED.value,
            "failed": ShipmentStatus.FAILED.value,
            # Courier-specific mappings to be extended in child classes
        }
        
        # Extend with courier-specific mappings
        status_mapping.update(self._get_status_mappings())
        
        return status_mapping.get(courier_status.lower(), ShipmentStatus.UNKNOWN.value)
    
    def _get_status_mappings(self) -> Dict[str, str]:
        """Get courier-specific status mappings"""
        return {}
        
    def _make_api_request(self, method, url, **kwargs):
        """
        Make API request with error handling
        """
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error: {err}")
            raise CourierAPIError(f"HTTP error: {err}")
        except requests.exceptions.ConnectionError as err:
            logger.error(f"Connection error: {err}")
            raise CourierAPIError(f"Connection error: {err}")
        except requests.exceptions.Timeout as err:
            logger.error(f"Timeout error: {err}")
            raise CourierAPIError(f"Timeout error: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error: {err}")
            raise CourierAPIError(f"Request error: {err}")