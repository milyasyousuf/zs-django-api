from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from zs.apps.core.renderers import CustomJSONRenderer
from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.services.shipment_service import ShipmentService
from zs.apps.courier_integrations.exceptions.courier_exceptions import CourierAPIError
from .serializers import (
    ShipmentSerializer,
    ShipmentCreateSerializer,
    CourierSerializer,
    TrackingHistorySerializer
)


class CourierViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for couriers"""
    queryset = Courier.objects.filter(is_active=True)
    serializer_class = CourierSerializer
    permission_classes = [AllowAny]
    renderer_classes = [CustomJSONRenderer]


class ShipmentViewSet(viewsets.ModelViewSet):
    """API endpoints for shipments"""
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [AllowAny]
    renderer_classes = [CustomJSONRenderer]

    
    def get_serializer_class(self):
        if self.action == 'create':
            return ShipmentCreateSerializer
        return ShipmentSerializer
    
    def create(self, request, *args, **kwargs):
        """Create shipment with waybill from courier API"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipment = ShipmentService.create_shipment(serializer.validated_data)
        result_serializer = ShipmentSerializer(shipment)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def track(self, request, pk=None):
        """Track shipment and update status"""
        shipment = self.get_object()
        tracking_data = ShipmentService.update_tracking_status(shipment)
        return Response(tracking_data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel shipment if supported by courier"""
        shipment = self.get_object()
        result = ShipmentService.cancel_shipment(shipment)
        return Response(result)
    
    
    @action(detail=True, methods=['get'])
    def label(self, request, pk=None):
        """Get waybill label PDF"""
        shipment = self.get_object()
        from zs.apps.courier_integrations.factories.courier_factory import CourierFactory
        courier_adapter = CourierFactory.get_courier(shipment.courier.code)
        label_pdf = courier_adapter.print_waybill_label(shipment.waybill_id)        
        response = HttpResponse(label_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="waybill_{shipment.waybill_id}.pdf"'
        return response
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get tracking history"""
        shipment = self.get_object()
        tracking_history = shipment.tracking_history.all()
        serializer = TrackingHistorySerializer(tracking_history, many=True)
        return Response(serializer.data)