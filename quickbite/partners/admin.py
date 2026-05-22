from django.contrib import admin
from .models import PartnerSubscription, RestaurantPartner, RestaurantEarnings


@admin.register(PartnerSubscription)
class PartnerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_months', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']


@admin.register(RestaurantPartner)
class RestaurantPartnerAdmin(admin.ModelAdmin):
    list_display = ['restaurant_name', 'owner_name', 'status', 'subscription', 'created_at']
    list_filter = ['status', 'cuisine_type', 'subscription']
    search_fields = ['restaurant_name', 'owner_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RestaurantEarnings)
class RestaurantEarningsAdmin(admin.ModelAdmin):
    list_display = ['partner', 'order_count', 'total_earnings', 'period_start', 'period_end']
    list_filter = ['period_start', 'period_end']
    search_fields = ['partner__restaurant_name']
