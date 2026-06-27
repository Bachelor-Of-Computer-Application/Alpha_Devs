"""Structured management hubs for the admin command center."""

from django.urls import reverse


def _url(name):
    try:
        return reverse(f"admin:{name}")
    except Exception:
        return "#"


def _hub_counts():
    """Lightweight counts for hub panels (single query batch where possible)."""
    from django.contrib.auth import get_user_model
    from orders.models import Order
    from partners.models import RestaurantPartner
    from payments.models import Coupon, Payment
    from restaurant.models import FoodItem, Restaurant, Review
    from riders.models import Delivery, Rider

    User = get_user_model()
    return {
        "users": User.objects.count(),
        "users_unverified": User.objects.filter(is_email_verified=False).count(),
        "groups": 0,  # filled below if needed
        "riders": Rider.objects.count(),
        "riders_pending": Rider.objects.filter(status="pending").count(),
        "deliveries": Delivery.objects.count(),
        "restaurants": Restaurant.objects.count(),
        "food_items": FoodItem.objects.count(),
        "reviews": Review.objects.count(),
        "payments": Payment.objects.count(),
        "payments_failed": Payment.objects.filter(status__in=("failed", "cancelled")).count(),
        "coupons": Coupon.objects.count(),
        "orders": Order.objects.count(),
        "orders_pending": Order.objects.filter(
            status__in=("pending", "confirmed", "preparing", "ready")
        ).count(),
        "partners": RestaurantPartner.objects.count(),
        "partners_pending": RestaurantPartner.objects.filter(status="pending").count(),
    }


def get_management_hubs():
    """Full-width management hub panels — replaces default Django app list."""
    c = _hub_counts()
    try:
        from django.contrib.auth.models import Group
        c["groups"] = Group.objects.count()
    except Exception:
        pass

    def panel(hub_id, title, subtitle, total, badge, actions):
        return {
            "id": hub_id,
            "title": title,
            "subtitle": subtitle,
            "total": total,
            "badge": badge,
            "actions": actions,
        }

    return [
        panel(
            "users",
            "User Management",
            "Customers, accounts, verification & permissions",
            c["users"],
            f"{c['users_unverified']} unverified",
            [
                {"label": "Manage Users", "url": _url("users_user_changelist"), "primary": True},
                {"label": "Add User", "url": _url("users_user_add")},
                {"label": "Groups", "url": _url("auth_group_changelist")},
                {"label": "Email Logs", "url": _url("users_emaillog_changelist")},
                {"label": "Analytics", "url": _url("qb_analytics")},
                {"label": "Export", "url": _url("qb_export_users_xlsx")},
            ],
        ),
        panel(
            "orders",
            "Order Management",
            "Live orders, tracking & customer support",
            c["orders"],
            f"{c['orders_pending']} pending",
            [
                {"label": "Manage Orders", "url": _url("orders_order_changelist"), "primary": True},
                {"label": "Add Order", "url": _url("orders_order_add")},
                {"label": "Order Items", "url": _url("orders_orderitem_changelist")},
                {"label": "Tracking", "url": _url("orders_ordertracking_changelist")},
                {"label": "Support Tickets", "url": _url("orders_supportticket_changelist")},
                {"label": "Export", "url": _url("qb_export_orders_xlsx")},
            ],
        ),
        panel(
            "payments",
            "Payment Management",
            "eSewa, Khalti, COD, invoices & coupons",
            c["payments"],
            f"{c['payments_failed']} failed",
            [
                {"label": "View Payments", "url": _url("payments_payment_changelist"), "primary": True},
                {"label": "Payment Methods", "url": _url("payments_paymentmethod_changelist")},
                {"label": "Invoices", "url": _url("payments_invoice_changelist")},
                {"label": "Coupons", "url": _url("payments_coupon_changelist")},
                {"label": "Add Coupon", "url": _url("payments_coupon_add")},
                {"label": "Export", "url": _url("qb_export_payments_xlsx")},
            ],
        ),
        panel(
            "restaurants",
            "Restaurant Management",
            "Listings, menus, reviews & cuisines",
            c["restaurants"],
            f"{c['food_items']} menu items",
            [
                {"label": "Manage Restaurants", "url": _url("restaurant_restaurant_changelist"), "primary": True},
                {"label": "Add Restaurant", "url": _url("restaurant_restaurant_add")},
                {"label": "Food Items", "url": _url("restaurant_fooditem_changelist")},
                {"label": "Reviews", "url": _url("restaurant_review_changelist")},
                {"label": "Cuisines", "url": _url("restaurant_cuisine_changelist")},
                {"label": "Export", "url": _url("qb_export_restaurants")},
            ],
        ),
        panel(
            "partners",
            "Partner Management",
            "Restaurant partners, subscriptions & earnings",
            c["partners"],
            f"{c['partners_pending']} pending approval",
            [
                {"label": "Restaurant Partners", "url": _url("partners_restaurantpartner_changelist"), "primary": True},
                {"label": "Subscription Plans", "url": _url("partners_subscriptionplan_changelist")},
                {"label": "Earnings", "url": _url("partners_restaurantearnings_changelist")},
                {"label": "Subscriptions", "url": _url("partners_partnersubscription_changelist")},
            ],
        ),
        panel(
            "riders",
            "Rider Management",
            "Fleet, deliveries, earnings & wallets",
            c["riders"],
            f"{c['riders_pending']} pending approval",
            [
                {"label": "Manage Riders", "url": _url("riders_rider_changelist"), "primary": True},
                {"label": "Add Rider", "url": _url("riders_rider_add")},
                {"label": "Deliveries", "url": _url("riders_delivery_changelist")},
                {"label": "Earnings", "url": _url("riders_riderearnings_changelist")},
                {"label": "Wallets", "url": _url("riders_riderwallet_changelist")},
                {"label": "Export", "url": _url("qb_export_riders")},
            ],
        ),
    ]


def get_admin_search_targets():
    """Global admin search — maps to changelist ?q= URLs."""
    return [
        {"key": "users", "label": "Users", "url": _url("users_user_changelist")},
        {"key": "orders", "label": "Orders", "url": _url("orders_order_changelist")},
        {"key": "restaurants", "label": "Restaurants", "url": _url("restaurant_restaurant_changelist")},
        {"key": "riders", "label": "Riders", "url": _url("riders_rider_changelist")},
        {"key": "payments", "label": "Payments", "url": _url("payments_payment_changelist")},
        {"key": "coupons", "label": "Coupons", "url": _url("payments_coupon_changelist")},
        {"key": "emails", "label": "Email Logs", "url": _url("users_emaillog_changelist")},
        {"key": "partners", "label": "Partners", "url": _url("partners_restaurantpartner_changelist")},
    ]


def get_quick_actions():
    """Toolbar shortcuts on the command center."""
    return [
        {
            "label": "Approve Rider",
            "url": f"{_url('riders_rider_changelist')}?status__exact=pending",
        },
        {
            "label": "Approve Restaurant",
            "url": f"{_url('partners_restaurantpartner_changelist')}?status__exact=pending",
        },
        {"label": "Create Coupon", "url": _url("payments_coupon_add")},
        {"label": "View Payments", "url": _url("payments_payment_changelist")},
        {"label": "Send Test Email", "url": _url("qb_email_health")},
        {"label": "Analytics Dashboard", "url": _url("qb_analytics")},
    ]
