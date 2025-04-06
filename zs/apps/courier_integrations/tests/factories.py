import factory
from factory.django import DjangoModelFactory
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.tracking import ShipmentTracking
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus
from django.utils import timezone


class CourierFactory(DjangoModelFactory):
    class Meta:
        model = Courier

    code = factory.Sequence(lambda n: f'courier_{n}')
    name = factory.Sequence(lambda n: f'Courier Provider {n}')
    is_active = True
    supports_cancellation = True
    config = factory.Dict({
        'api_url': 'https://api.example.com',
        'tracking_url': 'https://tracking.example.com',
        'pass_key': 'test_api_key',
    })


class ShipmentFactory(DjangoModelFactory):
    class Meta:
        model = Shipment

    reference_number = factory.Sequence(lambda n: f'REF{n:06d}')
    courier = factory.SubFactory(CourierFactory)
    waybill_id = factory.Sequence(lambda n: f'AWB{n:08d}')
    status = ShipmentStatus.PENDING.value
    last_tracking_update = None
    data = factory.Dict({
        'customer_name': 'Test Customer',
        'customer_id': 'CUST123',
        'shipping_date': '2025-04-01',
        'destination_country': 'UAE',
        'destination_city': 'Dubai',
        'postal_code': '12345',
        'address_line1': '123 Test Street',
        'phone_number': '+9715012345678',
        'package_count': 1,
        'weight': 2.5,
    })


class ShipmentTrackingFactory(DjangoModelFactory):
    class Meta:
        model = ShipmentTracking

    shipment = factory.SubFactory(ShipmentFactory)
    courier_status = 'shipment created'
    status = ShipmentStatus.PENDING.value
    location = 'Dubai, UAE'
    timestamp = factory.LazyFunction(timezone.now)
    description = 'Shipment has been created'
    raw_data = factory.Dict({
        'status': 'shipment created',
        'location': 'Dubai, UAE',
        'date': factory.LazyFunction(lambda: timezone.now().isoformat()),
    })