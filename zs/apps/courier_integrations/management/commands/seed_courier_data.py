import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.tracking import ShipmentTracking
from zs.apps.courier_integrations.enums.shipment_status import ShipmentStatus


class Command(BaseCommand):
    help = 'Seeds the database with test data for courier integrations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--couriers',
            type=int,
            default=3,
            help='Number of couriers to create'
        )
        
        parser.add_argument(
            '--shipments',
            type=int,
            default=10,
            help='Number of shipments to create'
        )
        
    def handle(self, *args, **options):
        num_couriers = options['couriers']
        num_shipments = options['shipments']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {num_couriers} couriers and {num_shipments} shipments...'))
        
        # Create couriers
        self._create_couriers(num_couriers)
        
        # Create shipments
        self._create_shipments(num_shipments)
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
    
    def _create_couriers(self, count):
        """Create sample courier records"""
        # Define some realistic courier data
        courier_data = [
            {
                'code': 'aramex',
                'name': 'ARAMEX',
                'supports_cancellation': True,
                'config': {
                    'api_url': 'https://api.example.com',
                    'tracking_url': 'https://tracking.example.com',
                    'pass_key': 'aramex_api_key'
                }
            },
            {
                'code': 'smsa',
                'name': 'SMSA Express',
                'supports_cancellation': True,
                'config': {
                    'api_url': 'https://api.smsa.com',
                    'tracking_url': 'https://tracking.smsa.com',
                    'pass_key': 'smsa_api_key'
                }
            },
            {
                'code': 'shipbox',
                'name': 'ShipBox',
                'supports_cancellation': False,
                'config': {
                    'api_url': 'https://api.shipbox.com',
                    'tracking_url': 'https://tracking.shipbox.com',
                    'pass_key': 'shipbox_api_key'
                }
            },
            {
                'code': 'dhl',
                'name': 'DHL Express',
                'supports_cancellation': True,
                'config': {
                    'api_url': 'https://api.dhl.com',
                    'tracking_url': 'https://tracking.dhl.com',
                    'pass_key': 'dhl_api_key'
                }
            },
            {
                'code': 'fedex',
                'name': 'FedEx',
                'supports_cancellation': True,
                'config': {
                    'api_url': 'https://api.fedex.com',
                    'tracking_url': 'https://tracking.fedex.com',
                    'pass_key': 'fedex_api_key'
                }
            }
        ]
        
        # Create or update courier records
        created_count = 0
        for i in range(min(count, len(courier_data))):
            data = courier_data[i]
            courier, created = Courier.objects.update_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'is_active': True,
                    'supports_cancellation': data['supports_cancellation'],
                    'config': data['config']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created courier: {courier.name}")
            else:
                self.stdout.write(f"Updated courier: {courier.name}")
        
        # Create additional random couriers if needed
        for i in range(created_count, count):
            code = f'courier_{i+1}'
            name = f'Courier Provider {i+1}'
            courier = Courier.objects.create(
                code=code,
                name=name,
                is_active=True,
                supports_cancellation=random.choice([True, False]),
                config={
                    'api_url': f'https://api.{code}.com',
                    'tracking_url': f'https://tracking.{code}.com',
                    'pass_key': f'{code}_api_key'
                }
            )
            self.stdout.write(f"Created courier: {courier.name}")
    
    def _create_shipments(self, count):
        """Create sample shipment records with tracking history"""
        # Get available couriers
        couriers = list(Courier.objects.filter(is_active=True))
        if not couriers:
            self.stdout.write(self.style.ERROR('No active couriers found. Please create couriers first.'))
            return
        
        # Countries and cities for random address generation
        countries = ['UAE', 'KSA', 'Qatar', 'Kuwait', 'Bahrain', 'Oman']
        cities = {
            'UAE': ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman'],
            'KSA': ['Riyadh', 'Jeddah', 'Dammam', 'Mecca'],
            'Qatar': ['Doha', 'Al Wakrah', 'Al Khor'],
            'Kuwait': ['Kuwait City', 'Hawalli', 'Salmiya'],
            'Bahrain': ['Manama', 'Riffa', 'Muharraq'],
            'Oman': ['Muscat', 'Salalah', 'Sohar']
        }
        
        # Possible shipment statuses
        statuses = [
            ShipmentStatus.PENDING.value,
            ShipmentStatus.PICKED_UP.value,
            ShipmentStatus.IN_TRANSIT.value,
            ShipmentStatus.OUT_FOR_DELIVERY.value,
            ShipmentStatus.DELIVERED.value
        ]
        
        # Create shipments
        for i in range(count):
            # Select random courier
            courier = random.choice(couriers)
            
            # Generate random shipment data
            reference_number = f'REF{random.randint(100000, 999999)}'
            waybill_id = f'{courier.code.upper()}{random.randint(10000000, 99999999)}'
            
            # Select random country and city
            country = random.choice(countries)
            city = random.choice(cities[country])
            
            # Select random status
            status = random.choice(statuses)
            
            # Create shipment
            shipment_data = {
                'customer_name': f'Customer {i+1}',
                'customer_id': f'CUST{random.randint(1000, 9999)}',
                'shipping_date': (timezone.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'destination_country': country,
                'destination_city': city,
                'postal_code': f'{random.randint(10000, 99999)}',
                'address_line1': f'{random.randint(1, 999)} Test Street',
                'address_line2': f'Suite {random.randint(100, 999)}',
                'phone_number': f'+{random.randint(1, 9)}71{random.randint(1000000, 9999999)}',
                'package_count': random.randint(1, 5),
                'weight': round(random.uniform(0.5, 20.0), 2),
                'description': f'Test Package {i+1}'
            }
            
            shipment = Shipment.objects.create(
                reference_number=reference_number,
                courier=courier,
                waybill_id=waybill_id,
                status=status,
                data=shipment_data,
                last_tracking_update=timezone.now() if status != ShipmentStatus.PENDING.value else None
            )
            self.stdout.write(f"Created shipment: {shipment.reference_number} with courier: {courier.name}")
            
            # Create tracking history for the shipment
            self._create_tracking_history(shipment, status)
    
    def _create_tracking_history(self, shipment, final_status):
        """Create tracking history for a shipment based on its final status"""
        # Status flow mapping
        status_flow = {
            ShipmentStatus.PENDING.value: [
                {'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'}
            ],
            ShipmentStatus.PICKED_UP.value: [
                {'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'},
                {'status': ShipmentStatus.PICKED_UP.value, 'courier_status': 'shipment picked up'}
            ],
            ShipmentStatus.IN_TRANSIT.value: [
                {'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'},
                {'status': ShipmentStatus.PICKED_UP.value, 'courier_status': 'shipment picked up'},
                {'status': ShipmentStatus.IN_TRANSIT.value, 'courier_status': 'in transit'}
            ],
            ShipmentStatus.OUT_FOR_DELIVERY.value: [
                {'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'},
                {'status': ShipmentStatus.PICKED_UP.value, 'courier_status': 'shipment picked up'},
                {'status': ShipmentStatus.IN_TRANSIT.value, 'courier_status': 'in transit'},
                {'status': ShipmentStatus.OUT_FOR_DELIVERY.value, 'courier_status': 'out for delivery'}
            ],
            ShipmentStatus.DELIVERED.value: [
                {'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'},
                {'status': ShipmentStatus.PICKED_UP.value, 'courier_status': 'shipment picked up'},
                {'status': ShipmentStatus.IN_TRANSIT.value, 'courier_status': 'in transit'},
                {'status': ShipmentStatus.OUT_FOR_DELIVERY.value, 'courier_status': 'out for delivery'},
                {'status': ShipmentStatus.DELIVERED.value, 'courier_status': 'delivered'}
            ]
        }
        
        # Get event flow for this shipment status
        events = status_flow.get(final_status, [{'status': ShipmentStatus.PENDING.value, 'courier_status': 'shipment created'}])
        
        # Calculate timestamps for events
        now = timezone.now()
        event_times = []
        days_span = min(len(events) * 2, 10)  # Span tracking over several days
        
        for i in range(len(events)):
            # Distribute events over time
            offset = timedelta(
                days=int((days_span * i) / len(events)),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            event_times.append(now - (days_span * timedelta(days=1)) + offset)
        
        # Create tracking events
        for i, event in enumerate(events):
            location = f"{shipment.data.get('destination_city', 'Unknown')}, {shipment.data.get('destination_country', 'Unknown')}"
            
            # For in-transit events, use transit hubs
            if event['status'] == ShipmentStatus.IN_TRANSIT.value:
                transit_hubs = ['Distribution Center', 'Transit Hub', 'Sorting Facility', 'Regional Hub']
                location = f"{random.choice(transit_hubs)}, {shipment.data.get('destination_country', 'Unknown')}"
            
            # Create tracking record
            ShipmentTracking.objects.create(
                shipment=shipment,
                courier_status=event['courier_status'],
                status=event['status'],
                location=location,
                timestamp=event_times[i],
                description=f"{event['courier_status'].capitalize()} at {location}",
                raw_data={
                    'status': event['courier_status'],
                    'location': location,
                    'date': event_times[i].isoformat()
                }
            )
            
        self.stdout.write(f"Created {len(events)} tracking events for shipment: {shipment.reference_number}")