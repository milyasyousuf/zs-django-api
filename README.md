# Courier Integration Framework

A unified integration framework for multiple courier services built with Django, providing a consistent interface for creating waybills, tracking shipments, printing labels, and more.

## Features

- **Unified Courier Interface**: Common API for all courier services
- **Extensible Architecture**: Easy to add new courier integrations with minimal code
- **Core Features**:
  - Create shipping waybills
  - Generate shipping labels
  - Track shipment status
  - Cancel shipments (when supported by the courier)
- **Status Standardization**: Maps different courier status codes to standardized system statuses
- **REST API**: Complete API for integration with other systems
- **Background Processing**: Automated tracking updates via Celery tasks

## Architecture

The system uses several design patterns to ensure a clean, maintainable codebase:

- **Interface-Based Design**: All couriers implement a common interface
- **Adapter Pattern**: Each courier has an adapter translating between system and courier APIs
- **Factory Pattern**: Creates courier instances based on configuration
- **Singleton Pattern**: Maintains a single instance per courier type

## Supported Couriers

- ARAMEX (implemented as proof of concept)
- Easily extensible to support additional couriers

## Requirements

- Python 3.8+
- Django 3.2+
- PostgreSQL / MySQL / SQLite
- Redis (for Celery)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zs-courier-integration.git
   cd zs-courier-integration
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Configure courier settings (see Configuration section)

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Configuration

### Courier Settings

Add courier configurations to your Django settings:

```python
# settings.py

# Courier class mapping
COURIER_MAPPING = {
    'aramex': 'zs.apps.courier_integrations.adapters.aramex.ARAMEXCourierAdapter',
    # Add other couriers as needed
}

# Courier-specific configurations
COURIER_CONFIG = {
    'ARAMEX': {
        'api_url': 'https://api.aramex.com/v1',
        'tracking_url': 'https://www.aramex.com/track/',
        'pass_key': 'your_api_key_here',
        # Other courier-specific settings
    },
    # Add configurations for other couriers
}
```

### Celery Configuration

Configure Celery for background tasks:

```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

```

## Setting Up for Testing

To quickly set up test data and configurations:

1. Run the setup script:
   ```bash
   python manage.py seed_courier_data
   ```

   This will create:
   - Test courier entries
   - Sample shipments
   - Initial tracking data

2. Or manually create courier entries via the Django admin:
   - Log in to the admin interface at `http://localhost:8000/admin/`
   - Navigate to "Couriers" and add entries for each courier with appropriate configurations

## API Endpoints

### Couriers

- `GET /api/couriers/` - List all active couriers

### Shipments

- `GET /api/shipments/` - List all shipments
- `POST /api/shipments/` - Create a new shipment
- `GET /api/shipments/{id}/` - Get shipment details
- `POST /api/shipments/{id}/track/` - Update tracking information
- `GET /api/shipments/{id}/history/` - Get tracking history
- `POST /api/shipments/{id}/cancel/` - Cancel a shipment
- `GET /api/shipments/{id}/label/` - Get waybill label PDF

## Creating a New Shipment

Example API request:

```json
POST /api/shipments/
{
  "courier_code": "aramex",
  "reference_number": "REF123456",
  "customer_name": "Test Customer",
  "shipping_date": "2025-04-06",
  "destination_country": "UAE",
  "destination_city": "Dubai",
  "postal_code": "12345",
  "address_line1": "123 Test Street",
  "phone_number": "+9715012345678",
  "weight": 2.5
}
```

## Adding a New Courier Integration

1. Create a new adapter class:

```python
# courier_integrations/adapters/new_courier.py
from zs.apps.courier_integrations.adapters.base import BaseCourierAdapter

class NewCourierAdapter(BaseCourierAdapter):
    """New Courier Implementation"""
    
    def create_waybill(self, shipment_data):
        # Implementation
        pass
        
    def print_waybill_label(self, waybill_id):
        # Implementation
        pass
    
    def track_shipment(self, waybill_id):
        # Implementation
        pass
    
    def _get_status_mappings(self):
        # Courier-specific status mappings
        return {
            "courier_status_1": "PENDING",
            "courier_status_2": "IN_TRANSIT",
            # etc.
        }
    
    def cancel_shipment(self, waybill_id):
        # Implementation if supported
        pass
```

2. Add the courier configuration to settings:

```python
# settings.py
COURIER_MAPPING['new_courier'] = 'zs.apps.courier_integrations.adapters.new_courier.NewCourierAdapter'

COURIER_CONFIG['NEW_COURIER'] = {
    'api_url': 'https://api.newcourier.com',
    'tracking_url': 'https://tracking.newcourier.com',
    # Other settings
}
```

3. Add the courier to the database:

```python
from zs.apps.courier_integrations.models.courier import Courier
Courier.objects.create(
    code='new_courier',
    name='New Courier Service',
    is_active=True,
    supports_cancellation=True
)
```

## Testing

Run unit tests:

```bash
python manage.py test zs.apps.courier_integrations.tests
```

## Management Commands

### Create Test Data

Creates sample data for testing:

```bash
python manage.py setup_courier_test_data
```

### Update All Shipments

Manually trigger tracking updates for all active shipments:

```bash
python manage.py update_all_shipments
```

## Celery Workers

Start Celery worker:

```bash
celery -A zs worker -l info
```

Start Celery beat scheduler:

```bash
celery -A zs beat -l info
```

## Running in Production

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure a proper database (PostgreSQL recommended)
3. Set up proper web server (Nginx + Gunicorn/uWSGI)
4. Set up Celery with supervisor or systemd
5. Configure proper logging
