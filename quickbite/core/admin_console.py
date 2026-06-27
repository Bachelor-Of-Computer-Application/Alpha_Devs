"""SaaS Operations Console — section data for the admin dashboard."""

from django.urls import reverse


def _url(name):
    try:
        return reverse(f"admin:{name}")
    except Exception:
        return "#"


def _order_status_counts():
    from orders.models import Order

    return {
        s: Order.objects.filter(status=s).count()
        for s, _ in Order.STATUS_CHOICES
    }


def _payment_by_method():
    from django.db.models import Count, Sum
    from payments.models import Payment

    methods = {}
    for row in (
        Payment.objects.filter(status="completed")
        .values("payment_method__name")
        .annotate(count=Count("id"), total=Sum("amount"))
    ):
        name = (row["payment_method__name"] or "unknown").lower()
        methods[name] = {"count": row["count"], "total": row["total"]}
    return methods


def get_admin_model_directory(admin_site, request):
    """Every registered Django admin model — Add + Manage links with live counts."""
    from django.apps import apps

    app_list = admin_site.get_app_list(request)
    app_icons = {
        "auth": "auth",
        "orders": "orders",
        "partners": "partners",
        "payments": "payments",
        "restaurant": "restaurants",
        "riders": "riders",
        "users": "users",
    }
    enriched = []
    for app in app_list:
        models = []
        for model in app.get("models", []):
            count = None
            try:
                model_cls = apps.get_model(app["app_label"], model["object_name"])
                count = model_cls.objects.count()
            except Exception:
                pass
            models.append({**model, "count": count})
        if models:
            enriched.append({
                **app,
                "icon": app_icons.get(app["app_label"], "default"),
                "models": models,
                "model_count": len(models),
            })
    return enriched


def get_console_sections():
    """Build all 8 dashboard sections for the operations console."""
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Sum
    from orders.models import Order, SupportTicket
    from partners.models import RestaurantPartner
    from payments.models import Coupon, Payment
    from restaurant.models import FoodItem, Restaurant, Review
    from riders.models import Delivery, Rider
    from users.models import EmailLog

    User = get_user_model()
    orders = Order.objects
    payments = Payment.objects
    status = _order_status_counts()
    pay_methods = _payment_by_method()

    total_pay = payments.count()
    completed_pay = payments.filter(status="completed").count()
    failed_pay = payments.filter(status__in=("failed", "cancelled")).count()
    pay_success_rate = round((completed_pay / total_pay) * 100, 1) if total_pay else 0
    pay_fail_rate = round((failed_pay / total_pay) * 100, 1) if total_pay else 0

    total_users = User.objects.count()
    verified = User.objects.filter(is_email_verified=True).count()
    retention = round((verified / total_users) * 100, 1) if total_users else 0

    staff_count = User.objects.filter(is_staff=True).count()
    customers = User.objects.filter(role="CUSTOMER").count()

    emails_sent = EmailLog.objects.filter(status="sent").count()
    emails_failed = EmailLog.objects.filter(status="failed").count()
    email_total = emails_sent + emails_failed
    email_success_pct = round((emails_sent / email_total) * 100, 1) if email_total else 0

    return {
        "operations_cards": [
            {
                "id": "orders",
                "icon": "orders",
                "title": "Orders",
                "total": orders.count(),
                "stats": [
                    {"label": "Pending", "value": status.get("pending", 0)},
                    {"label": "Preparing", "value": status.get("preparing", 0)},
                    {"label": "Delivered", "value": status.get("delivered", 0)},
                ],
                "actions": [
                    {"label": "Manage Orders", "url": _url("orders_order_changelist"), "primary": True},
                    {"label": "Track Orders", "url": _url("orders_ordertracking_changelist")},
                    {"label": "Export", "url": _url("qb_export_orders_xlsx")},
                    {"label": "Analytics", "url": _url("qb_analytics")},
                ],
            },
            {
                "id": "restaurants",
                "icon": "restaurants",
                "title": "Restaurants",
                "total": Restaurant.objects.count(),
                "stats": [
                    {"label": "Active", "value": Restaurant.objects.filter(is_active=True, is_approved=True).count()},
                    {"label": "Menu items", "value": FoodItem.objects.count()},
                    {"label": "Reviews", "value": Review.objects.count()},
                ],
                "actions": [
                    {"label": "Manage", "url": _url("restaurant_restaurant_changelist"), "primary": True},
                    {"label": "Add New", "url": _url("restaurant_restaurant_add")},
                    {"label": "Food Items", "url": _url("restaurant_fooditem_changelist")},
                    {"label": "Export", "url": _url("qb_export_restaurants")},
                ],
            },
            {
                "id": "riders",
                "icon": "riders",
                "title": "Riders",
                "total": Rider.objects.count(),
                "stats": [
                    {"label": "Online", "value": Rider.objects.filter(is_available=True).count()},
                    {"label": "Pending", "value": Rider.objects.filter(status="pending").count()},
                    {"label": "Deliveries", "value": Delivery.objects.count()},
                ],
                "actions": [
                    {"label": "Manage Riders", "url": _url("riders_rider_changelist"), "primary": True},
                    {"label": "Deliveries", "url": _url("riders_delivery_changelist")},
                    {"label": "Export", "url": _url("qb_export_riders")},
                ],
            },
            {
                "id": "users",
                "icon": "users",
                "title": "Users",
                "total": total_users,
                "stats": [
                    {"label": "Customers", "value": customers},
                    {"label": "Unverified", "value": User.objects.filter(is_email_verified=False).count()},
                    {"label": "Admins", "value": staff_count},
                ],
                "actions": [
                    {"label": "Manage Users", "url": _url("users_user_changelist"), "primary": True},
                    {"label": "Email Logs", "url": _url("users_emaillog_changelist")},
                    {"label": "Export", "url": _url("qb_export_users_xlsx")},
                ],
            },
            {
                "id": "payments",
                "icon": "payments",
                "title": "Payments",
                "total": total_pay,
                "stats": [
                    {"label": "Completed", "value": completed_pay},
                    {"label": "Pending", "value": payments.filter(status="pending").count()},
                    {"label": "Failed", "value": failed_pay},
                ],
                "actions": [
                    {"label": "View Payments", "url": _url("payments_payment_changelist"), "primary": True},
                    {"label": "Invoices", "url": _url("payments_invoice_changelist")},
                    {"label": "Export", "url": _url("qb_export_payments_xlsx")},
                ],
            },
            {
                "id": "coupons",
                "icon": "coupons",
                "title": "Coupons",
                "total": Coupon.objects.count(),
                "stats": [
                    {"label": "Active", "value": Coupon.objects.filter(is_active=True).count()},
                    {"label": "Inactive", "value": Coupon.objects.filter(is_active=False).count()},
                ],
                "actions": [
                    {"label": "Manage", "url": _url("payments_coupon_changelist"), "primary": True},
                    {"label": "Create", "url": _url("payments_coupon_add")},
                ],
            },
            {
                "id": "reviews",
                "icon": "reviews",
                "title": "Reviews",
                "total": Review.objects.count(),
                "stats": [{"label": "All time", "value": Review.objects.count()}],
                "actions": [
                    {"label": "Manage Reviews", "url": _url("restaurant_review_changelist"), "primary": True},
                ],
            },
            {
                "id": "support",
                "icon": "support",
                "title": "Support",
                "total": SupportTicket.objects.count(),
                "stats": [
                    {"label": "Open", "value": SupportTicket.objects.filter(status="open").count()},
                    {"label": "Closed", "value": SupportTicket.objects.filter(status="closed").count()},
                ],
                "actions": [
                    {"label": "Tickets", "url": _url("orders_supportticket_changelist"), "primary": True},
                ],
            },
        ],
        "payment_center": {
            "total_revenue": payments.filter(status="completed").aggregate(t=Sum("amount"))["t"] or 0,
            "today_revenue_key": "daily",
            "pending": payments.filter(status="pending").count(),
            "failed": failed_pay,
            "refunds": payments.filter(status="refunded").count(),
            "success_rate": pay_success_rate,
            "failure_rate": pay_fail_rate,
            "volume": total_pay,
            "khalti": pay_methods.get("khalti", {"count": 0, "total": 0}),
            "esewa": pay_methods.get("esewa", {"count": 0, "total": 0}),
            "cod": pay_methods.get("cod", {"count": 0, "total": 0}),
        },
        "user_center": [
            {
                "title": "Customers",
                "total": customers,
                "active": User.objects.filter(role="CUSTOMER", is_active=True).count(),
                "pending": User.objects.filter(role="CUSTOMER", is_email_verified=False).count(),
                "manage_url": _url("users_user_changelist"),
                "export_url": _url("qb_export_users_xlsx"),
            },
            {
                "title": "Restaurants",
                "total": Restaurant.objects.count(),
                "active": Restaurant.objects.filter(is_active=True).count(),
                "pending": RestaurantPartner.objects.filter(status="pending").count(),
                "manage_url": _url("restaurant_restaurant_changelist"),
                "approve_url": f"{_url('partners_restaurantpartner_changelist')}?status__exact=pending",
            },
            {
                "title": "Riders",
                "total": Rider.objects.count(),
                "active": Rider.objects.filter(status__in=("approved", "active")).count(),
                "pending": Rider.objects.filter(status="pending").count(),
                "manage_url": _url("riders_rider_changelist"),
                "approve_url": f"{_url('riders_rider_changelist')}?status__exact=pending",
            },
            {
                "title": "Admins",
                "total": staff_count,
                "active": User.objects.filter(is_staff=True, is_active=True).count(),
                "pending": 0,
                "manage_url": _url("users_user_changelist"),
            },
            {
                "title": "Partners",
                "total": RestaurantPartner.objects.count(),
                "active": RestaurantPartner.objects.filter(status="approved").count(),
                "pending": RestaurantPartner.objects.filter(status="pending").count(),
                "manage_url": _url("partners_restaurantpartner_changelist"),
                "approve_url": f"{_url('partners_restaurantpartner_changelist')}?status__exact=pending",
            },
            {
                "title": "Email Logs",
                "total": EmailLog.objects.count(),
                "active": emails_sent,
                "pending": emails_failed,
                "manage_url": _url("users_emaillog_changelist"),
            },
        ],
        "approval_items": [
            {
                "title": "Restaurant Approvals",
                "count": RestaurantPartner.objects.filter(status="pending").count(),
                "url": f"{_url('partners_restaurantpartner_changelist')}?status__exact=pending",
            },
            {
                "title": "Rider Approvals",
                "count": Rider.objects.filter(status="pending").count(),
                "url": f"{_url('riders_rider_changelist')}?status__exact=pending",
            },
            {
                "title": "Email Verification",
                "count": User.objects.filter(is_email_verified=False, role="CUSTOMER").count(),
                "url": f"{_url('users_user_changelist')}?is_email_verified__exact=0",
            },
            {
                "title": "Pending Reviews",
                "count": Review.objects.filter(rating__lte=2).count(),
                "url": _url("restaurant_review_changelist"),
            },
            {
                "title": "Support Escalations",
                "count": SupportTicket.objects.filter(status="open").count(),
                "url": _url("orders_supportticket_changelist"),
            },
        ],
        "funnel_metrics": {
            "checkout_started": orders.filter(status__in=("pending", "confirmed", "preparing", "ready", "delivered")).count(),
            "orders_placed": orders.count(),
            "payments_initiated": total_pay,
            "payments_completed": completed_pay,
            "restaurants_pending": RestaurantPartner.objects.filter(status="pending").count(),
            "restaurants_approved": RestaurantPartner.objects.filter(status="approved").count(),
            "riders_pending": Rider.objects.filter(status="pending").count(),
            "riders_approved": Rider.objects.filter(status__in=("approved", "active")).count(),
            "retention_pct": retention,
        },
        "email_center": {
            "success_pct": email_success_pct,
            "sent": emails_sent,
            "failed": emails_failed,
            "health_url": _url("qb_email_health"),
            "logs_url": _url("users_emaillog_changelist"),
        },
    }
