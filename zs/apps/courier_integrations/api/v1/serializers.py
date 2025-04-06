from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.tracking import ShipmentTracking
from rest_framework import serializers

class CourierSerializer(serializers.ModelSerializer):
    """Courier serializer"""
    class Meta:
        model = Courier
        fields = ['id', 'code', 'name', 'supports_cancellation']


class ShipmentSerializer(serializers.ModelSerializer):
    """Shipment details serializer"""
    courier = CourierSerializer(read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'reference_number', 'courier', 'waybill_id', 
            'status', 'created_at', 'updated_at', 'last_tracking_update'
        ]


class ShipmentCreateSerializer(serializers.Serializer):
    """Serializer for creating new shipments"""
    courier_code = serializers.CharField()
    reference_number = serializers.CharField()
    customer_name = serializers.CharField()
    customer_id = serializers.CharField(required=False, allow_blank=True)
    shipping_date = serializers.DateField()
    destination_country = serializers.CharField()
    destination_city = serializers.CharField()
    postal_code = serializers.CharField(required=False, allow_blank=True)
    address_line1 = serializers.CharField()
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField()
    alternative_phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    po_box = serializers.CharField(required=False, allow_blank=True)
    package_count = serializers.IntegerField(min_value=1, default=1)
    weight = serializers.FloatField(min_value=0.1)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_courier_code(self, value):
        """Validate courier exists and is active"""
        try:
            Courier.objects.get(code=value, is_active=True)
        except Courier.DoesNotExist:
            raise serializers.ValidationError(f"Courier with code '{value}' does not exist or is inactive")
        return value


class TrackingHistorySerializer(serializers.ModelSerializer):
    """Serializer for shipment tracking history"""
    class Meta:
        model = ShipmentTracking
        fields = [
            'id', 'courier_status', 'status', 'location', 
            'timestamp', 'description', 'created_at'
        ]