from zs.apps.courier_integrations.interfaces.courier_interface import CourierInterface
from django.utils.module_loading import import_string

class CourierFactory:
    _instances = {}
    
    @classmethod
    def get_courier(cls, courier_code: str) -> CourierInterface:
        """
        Get or create courier instance based on courier code
        Implements Singleton pattern per courier type
        """
        if courier_code not in cls._instances:
            from django.conf import settings
            courier_path = settings.COURIER_MAPPING.get(courier_code)
            if not courier_path:
                raise ValueError(f"Unsupported courier: {courier_code}")
            
            courier_class = import_string(courier_path)
            cls._instances[courier_code] = courier_class()
            
        return cls._instances[courier_code]