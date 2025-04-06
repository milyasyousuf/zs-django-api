class CourierAPIError(Exception):
    """Exception raised when a courier API returns an error"""
    pass


class CourierNotImplementedError(Exception):
    """Exception raised when a courier functionality is not implemented"""
    pass


class CourierConfigError(Exception):
    """Exception raised when courier configuration is invalid or missing"""
    pass