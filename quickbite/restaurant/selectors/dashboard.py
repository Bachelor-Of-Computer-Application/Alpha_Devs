"""Read-only queries for restaurant partner dashboards."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractHour
from django.utils import timezone

from orders.models import Order, OrderItem
from restaurant.models import FoodItem, Review


def get_restaurant_for_user(user):
    """Resolve Restaurant from owner or partner profile."""
    from partners.models import RestaurantPartner

    restaurant = user.owned_restaurants.first()
    if restaurant:
        return restaurant
    try:
        partner = RestaurantPartner.objects.select_related("restaurant").get(user=user)
        return partner.restaurant
    except RestaurantPartner.DoesNotExist:
        return None


def get_dashboard_stats(restaurant):
    if not restaurant:
        return {}

    now = timezone.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    orders = Order.objects.filter(restaurant=restaurant)
    total = orders.count()
    pending = orders.filter(status__in=["pending", "confirmed", "preparing"]).count()
    completed = orders.filter(status="delivered").count()
    cancelled = orders.filter(status="cancelled").count()

    earnings = (
        orders.filter(status="delivered", payment_status="paid").aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0")
    )
    daily = orders.filter(created_at__date=today, status="delivered").aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")
    weekly = orders.filter(
        created_at__date__gte=week_ago, status="delivered"
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    monthly = orders.filter(
        created_at__date__gte=month_ago, status="delivered"
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")

    cancel_rate = round((cancelled / total * 100), 1) if total else 0

    top_foods = (
        OrderItem.objects.filter(order__restaurant=restaurant)
        .values("food_item__name")
        .annotate(qty=Sum("quantity"))
        .order_by("-qty")[:5]
    )

    peak_hours = list(
        orders.annotate(hour=ExtractHour("created_at"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    reviews = Review.objects.filter(restaurant=restaurant).order_by("-created_at")[:5]
    avg_rating = Review.objects.filter(restaurant=restaurant).aggregate(
        avg=Avg("rating")
    )["avg"]

    return {
        "total_orders": total,
        "pending_orders": pending,
        "completed_orders": completed,
        "cancelled_orders": cancelled,
        "earnings": earnings,
        "daily_revenue": daily,
        "weekly_revenue": weekly,
        "monthly_revenue": monthly,
        "cancellation_rate": cancel_rate,
        "top_foods": top_foods,
        "peak_hours": peak_hours,
        "recent_reviews": reviews,
        "avg_rating": round(avg_rating, 1) if avg_rating else 0,
        "menu_count": FoodItem.objects.filter(restaurant=restaurant).count(),
    }
