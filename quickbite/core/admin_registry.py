"""Register all models on the custom QuickBite admin site."""

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from core.admin_site import admin_site


def register_quickbite_admin():
    from orders.admin import OrderAdmin, OrderItemAdmin, OrderTrackingAdmin, SupportTicketAdmin
    from orders.models import Order, OrderItem, OrderTracking, SupportTicket
    from partners.admin import (
        PartnerSubscriptionAdmin,
        RestaurantEarningsAdmin,
        RestaurantPartnerAdmin,
    )
    from partners.models import PartnerSubscription, RestaurantEarnings, RestaurantPartner
    from payments.admin import CouponAdmin, InvoiceAdmin, PaymentAdmin, PaymentMethodAdmin
    from payments.models import Coupon, Invoice, Payment, PaymentMethod
    from restaurant.admin import (
        CuisineAdmin,
        FavoriteAdmin,
        FoodItemAdmin,
        RestaurantAdmin,
        ReviewAdmin,
    )
    from restaurant.models import Cuisine, Favorite, FoodItem, Restaurant, Review
    from riders.admin import DeliveryAdmin, RiderAdmin, RiderEarningsAdmin
    from riders.models import Delivery, Rider, RiderEarnings

    registry = [
        (Cuisine, CuisineAdmin),
        (Restaurant, RestaurantAdmin),
        (FoodItem, FoodItemAdmin),
        (Favorite, FavoriteAdmin),
        (Review, ReviewAdmin),
        (Order, OrderAdmin),
        (OrderItem, OrderItemAdmin),
        (OrderTracking, OrderTrackingAdmin),
        (SupportTicket, SupportTicketAdmin),
        (PartnerSubscription, PartnerSubscriptionAdmin),
        (RestaurantPartner, RestaurantPartnerAdmin),
        (RestaurantEarnings, RestaurantEarningsAdmin),
        (Rider, RiderAdmin),
        (Delivery, DeliveryAdmin),
        (RiderEarnings, RiderEarningsAdmin),
        (PaymentMethod, PaymentMethodAdmin),
        (Payment, PaymentAdmin),
        (Invoice, InvoiceAdmin),
        (Coupon, CouponAdmin),
        (User, UserAdmin),
        (Group, GroupAdmin),
    ]

    for model, admin_class in registry:
        try:
            admin_site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass
