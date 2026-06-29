"""Rider delivery assignment, earnings, and location helpers."""

import math
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from orders.models import Order, OrderTracking
from restaurant.services.order_service import update_order_status
from riders.models import Delivery, Rider, RiderWallet


def _distance_km(lat1, lng1, lat2, lng2):
    """Haversine distance — free, no external API."""
    if None in (lat1, lng1, lat2, lng2):
        return 9999.0
    r = 6371
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lng2) - float(lng1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_or_create_wallet(rider):
    wallet, _ = RiderWallet.objects.get_or_create(rider=rider)
    return wallet


def available_orders_for_rider(rider):
    """Orders ready for pickup, sorted by distance to restaurant."""
    qs = Order.objects.filter(
        status='ready',
        rider__isnull=True,
    ).select_related('restaurant')

    orders = list(qs)
    if rider.current_latitude and rider.current_longitude:
        orders.sort(
            key=lambda o: _distance_km(
                rider.current_latitude,
                rider.current_longitude,
                o.restaurant.latitude or 27.7172,
                o.restaurant.longitude or 85.3240,
            )
        )
    return orders


def create_delivery_offer(order, rider):
    """Create a pending delivery offer for a rider."""
    return Delivery.objects.get_or_create(
        order=order,
        rider=rider,
        defaults={
            "status": "pending",
            "pickup_address": order.restaurant.location,
            "delivery_address": order.delivery_address,
            "delivery_contact": order.delivery_contact,
        },
    )[0]


def accept_delivery(delivery, rider):
    if delivery.rider_id != rider.id:
        raise ValueError("Not your delivery.")
    if delivery.status != "pending":
        raise ValueError("Delivery already processed.")

    delivery.status = "accepted"
    delivery.accepted_at = timezone.now()
    delivery.save()

    order = delivery.order
    order.rider = rider
    order.save(update_fields=['rider', 'updated_at'])
    OrderTracking.objects.create(
        order=order,
        status='rider_assigned',
        description=f'Rider {rider.full_name} accepted delivery',
    )
    try:
        from users.email_dispatcher import dispatch_rider_assigned
        dispatch_rider_assigned(order, rider)
    except Exception:
        pass
    return delivery


def reject_delivery(delivery, rider):
    if delivery.rider_id != rider.id:
        raise ValueError("Not your delivery.")
    delivery.rejected = True
    delivery.status = "cancelled"
    delivery.save()
    order = delivery.order
    if order.rider_id == rider.id:
        order.rider = None
        order.save(update_fields=["rider", "updated_at"])
    return delivery


def mark_in_transit(delivery, rider):
    if delivery.rider_id != rider.id:
        raise ValueError("Not your delivery.")
    delivery.status = "in_transit"
    delivery.save(update_fields=["status", "updated_at"])
    update_order_status(delivery.order, "in_transit", rider.user, "Order on the way")
    return delivery


def mark_picked_up(delivery, rider):
    if delivery.rider_id != rider.id:
        raise ValueError("Not your delivery.")
    delivery.status = "picked_up"
    delivery.picked_up_at = timezone.now()
    delivery.save()
    update_order_status(delivery.order, "picked_up", rider.user, "Order picked up")
    return delivery


def mark_delivered(delivery, rider):
    if delivery.rider_id != rider.id:
        raise ValueError("Not your delivery.")
    order = delivery.order
    if order.status == "picked_up":
        update_order_status(order, "in_transit", rider.user, "Rider en route to customer")
        order.refresh_from_db()

    delivery.status = "delivered"
    delivery.delivered_at = timezone.now()
    delivery.save()
    order.rider_confirmed_at = timezone.now()
    update_order_status(order, "delivered", rider.user, "Rider confirmed delivery")

    commission = order.rider_commission or (order.delivery_fee * Decimal("0.8"))
    order.rider_commission = commission
    order.platform_fee = order.delivery_fee - commission
    order.delivered_at = timezone.now()
    order.save(update_fields=["rider_commission", "platform_fee", "rider_confirmed_at", "delivered_at"])

    from orders.services.order_service import mark_cod_paid_on_delivery
    from payments.models import Payment

    cod_payment = Payment.objects.filter(
        order=order,
        payment_method__name="cod",
        status="pending",
    ).first()
    if cod_payment:
        mark_cod_paid_on_delivery(order)
        cod_payment.status = "completed"
        cod_payment.completed_at = timezone.now()
        cod_payment.save(update_fields=["status", "completed_at", "updated_at"])
        try:
            from users.email_dispatcher import dispatch_payment_event
            dispatch_payment_event(cod_payment, "success")
        except Exception:
            pass

    try:
        from users.email_dispatcher import dispatch_rider_delivery_completed
        dispatch_rider_delivery_completed(order, rider)
    except Exception:
        pass

    wallet = get_or_create_wallet(rider)
    wallet.total_earnings += commission
    wallet.pending_earnings += commission
    wallet.withdrawable_balance += commission
    wallet.delivery_count += 1
    wallet.save()

    rider.total_earnings += commission
    rider.save(update_fields=["total_earnings"])
    return delivery


def customer_confirm_delivery(order, user):
    if order.user_id != user.id:
        raise ValueError("Not your order.")
    if order.status != "delivered":
        raise ValueError("Order not delivered yet.")
    order.customer_confirmed_at = timezone.now()
    order.save(update_fields=["customer_confirmed_at"])
    OrderTracking.objects.create(
        order=order,
        status="customer_confirmed",
        description="Customer confirmed delivery receipt.",
    )
    return order
