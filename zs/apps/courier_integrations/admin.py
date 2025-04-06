from django.contrib import admin

from zs.apps.courier_integrations.models.courier import Courier
from zs.apps.courier_integrations.models.shipment import Shipment
from zs.apps.courier_integrations.models.tracking import ShipmentTracking


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'supports_cancellation')
    list_filter = ('is_active', 'supports_cancellation')
    search_fields = ('name', 'code')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'is_active', 'supports_cancellation')
        }),
        ('Configuration', {
            'classes': ('collapse',),
            'fields': ('config',)
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )


class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    readonly_fields = ('courier_status', 'status', 'location', 'timestamp', 'description', 'raw_data', 'created_at')
    can_delete = False
    show_change_link = True


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'courier', 'status', 'last_tracking_update', 'created_at')
    list_filter = ('status', 'courier')
    search_fields = ('reference_number', 'courier__name', 'waybill_id')
    readonly_fields = ('created_at', 'updated_at', 'last_tracking_update')
    ordering = ('-created_at',)
    inlines = [ShipmentTrackingInline]
    fieldsets = (
        (None, {
            'fields': ('reference_number', 'courier', 'waybill_id', 'status')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'last_tracking_update')
        }),
        ('Additional Data', {
            'classes': ('collapse',),
            'fields': ('data',)
        }),
    )


@admin.register(ShipmentTracking)
class ShipmentTrackingAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'courier_status', 'status', 'location', 'timestamp')
    list_filter = ('status', 'shipment__courier')
    search_fields = ('shipment__reference_number', 'courier_status', 'status', 'location')
    readonly_fields = ('created_at',)
    ordering = ('-timestamp',)
    fieldsets = (
        (None, {
            'fields': ('shipment', 'courier_status', 'status', 'location', 'timestamp', 'description')
        }),
        ('Raw Data', {
            'classes': ('collapse',),
            'fields': ('raw_data',)
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        }),
    )
