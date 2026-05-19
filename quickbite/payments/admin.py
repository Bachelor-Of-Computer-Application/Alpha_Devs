from django.contrib import admin
from .models import PaymentMethod, Payment, Invoice, Coupon


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_method', 'payment_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_type', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'invoice_type', 'total', 'created_at']
    list_filter = ['invoice_type', 'created_at']
    search_fields = ['invoice_number', 'user__username']
    readonly_fields = ['created_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']
