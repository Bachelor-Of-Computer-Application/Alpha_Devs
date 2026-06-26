"""Restaurant order workflow."""

from django.utils import timezone

from orders.models import Order, OrderTracking


VALID_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["preparing", "cancelled"],
    "preparing": ["ready", "cancelled"],
    "ready": ["picked_up", "cancelled"],
    "picked_up": ["in_transit"],
    "in_transit": ["delivered"],
}


def can_transition(order, new_status):
    allowed = VALID_TRANSITIONS.get(order.status, [])
    return new_status in allowed or new_status == "cancelled"


def update_order_status(order, new_status, user, note=""):
    if not can_transition(order, new_status) and new_status != "cancelled":
        raise ValueError(f"Cannot change status from {order.status} to {new_status}")

    order.status = new_status
    if new_status == "confirmed":
        order.confirmed_at = timezone.now()
    if new_status == "delivered":
        order.delivered_at = timezone.now()
    order.save()

    OrderTracking.objects.create(
        order=order,
        status=new_status,
        description=note or f"Status updated to {new_status}",
    )
    try:
        from users.email_dispatcher import dispatch_order_status
        dispatch_order_status(order, new_status, note)
    except Exception:
        pass
    return order


def assign_rider(order, rider):
    order.rider = rider
    order.save(update_fields=["rider", "updated_at"])
    OrderTracking.objects.create(
        order=order,
        status="rider_assigned",
        description=f"Rider {rider.full_name} assigned",
    )
    try:
        from users.email_dispatcher import dispatch_rider_assigned
        dispatch_rider_assigned(order, rider)
    except Exception:
        pass
    return order
