# courier_integration/interfaces/courier_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class CourierInterface(ABC):
    """Abstract interface for all courier implementations"""
    
    @abstractmethod
    def create_waybill(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a waybill for a shipment.
        
        Args:
            shipment_data: Dictionary containing shipment details
            
        Returns:
            Dict containing waybill information including waybill_id
        """
        pass
    
    @abstractmethod
    def print_waybill_label(self, waybill_id: str) -> bytes:
        """
        Generate waybill label as PDF bytes.
        
        Args:
            waybill_id: The waybill identifier
            
        Returns:
            Bytes containing PDF data of the label
        """
        pass
    
    @abstractmethod
    def track_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """
        Track shipment status.
        
        Args:
            waybill_id: The waybill identifier
            
        Returns:
            Dict containing tracking information
        """
        pass
    
    @abstractmethod
    def map_status(self, courier_status: str) -> str:
        """
        Map courier-specific status to system status.
        
        Args:
            courier_status: Status string from courier
            
        Returns:
            Standardized system status
        """
        pass
    
    def cancel_shipment(self, waybill_id: str) -> Dict[str, Any]:
        """
        Optional method to cancel shipment.
        
        Args:
            waybill_id: The waybill identifier
            
        Returns:
            Dict containing cancellation result
        
        Raises:
            NotImplementedError: If courier doesn't support cancellation
        """
        raise NotImplementedError("This courier does not support cancellation")