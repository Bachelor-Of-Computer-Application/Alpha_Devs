"""Operational metrics for Django admin dashboard."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractHour, TruncDate
from django.utils import timezone

User = get_user_model()


def get_admin_dashboard_context():
    """Aggregate KPIs for admin index and analytics page."""
    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    from orders.models import Order, OrderItem
    from partners.models import RestaurantPartner
    from restaurant.models import FoodItem, Restaurant
    from riders.models import Delivery, Rider

    orders = Order.objects.all()
    total_orders = orders.count()
    delivered = orders.filter(status="delivered").count()
    cancelled = orders.filter(status="cancelled").count()
    completed_deliveries = Delivery.objects.filter(status="delivered").count()

    daily_orders_qs = (
        orders.filter(created_at__date=today)
        .aggregate(count=Count("id"), revenue=Sum("total_amount"))
    )
    weekly_sales = orders.filter(created_at__date__gte=week_ago).aggregate(
        total=Sum("total_amount"), count=Count("id")
    )
    monthly_sales = orders.filter(created_at__date__gte=month_ago).aggregate(
        total=Sum("total_amount"), count=Count("id")
    )

    avg_order = orders.aggregate(avg=Avg("total_amount"))["avg"] or Decimal("0")

    success_rate = 0.0
    if total_orders:
        success_rate = round((delivered / total_orders) * 100, 1)

    top_restaurants = (
        orders.values("restaurant__name")
        .annotate(order_count=Count("id"), revenue=Sum("total_amount"))
        .order_by("-order_count")[:5]
    )

    top_foods = (
        OrderItem.objects.values("food_item__name", "food_item__restaurant__name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:5]
    )

    orders_by_day = list(
        orders.filter(created_at__gte=now - timedelta(days=14))
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    peak_hours = list(
        orders.exclude(status="cancelled")
        .annotate(hour=ExtractHour("created_at"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    return {
        "qb_total_users": User.objects.count(),
        "qb_total_restaurants": Restaurant.objects.count(),
        "qb_total_riders": Rider.objects.count(),
        "qb_total_orders": total_orders,
        "qb_pending_restaurants": RestaurantPartner.objects.filter(status="pending").count(),
        "qb_pending_riders": Rider.objects.filter(status="pending").count(),
        "qb_completed_deliveries": completed_deliveries,
        "qb_delivered_orders": delivered,
        "qb_cancelled_orders": cancelled,
        "qb_daily_orders": daily_orders_qs.get("count") or 0,
        "qb_daily_revenue": daily_orders_qs.get("revenue") or Decimal("0"),
        "qb_weekly_sales": weekly_sales.get("total") or Decimal("0"),
        "qb_weekly_order_count": weekly_sales.get("count") or 0,
        "qb_monthly_sales": monthly_sales.get("total") or Decimal("0"),
        "qb_monthly_order_count": monthly_sales.get("count") or 0,
        "qb_avg_order_value": avg_order,
        "qb_delivery_success_rate": success_rate,
        "qb_top_restaurants": top_restaurants,
        "qb_top_foods": top_foods,
        "qb_orders_by_day": orders_by_day,
        "qb_peak_hours": peak_hours,
        "qb_approved_restaurants": Restaurant.objects.filter(is_approved=True).count(),
    }
