from django.contrib import admin
from .models import Rider, Delivery, RiderEarnings


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'vehicle_type', 'status', 'is_available', 'registration_fee_paid']
    list_filter = ['status', 'vehicle_type', 'is_available', 'registration_fee_paid']
    search_fields = ['full_name', 'phone', 'vehicle_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'rider', 'order', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['rider__full_name', 'delivery_address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RiderEarnings)
class RiderEarningsAdmin(admin.ModelAdmin):
    list_display = ['rider', 'delivery_count', 'total_earnings', 'period_start', 'period_end']
    list_filter = ['period_start', 'period_end']
    search_fields = ['rider__full_name']
