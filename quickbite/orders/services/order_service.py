"""Create orders from checkout cart data."""
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem, OrderTracking
from orders.services.coupon_service import validate_coupon
from restaurant.models import FoodItem, Restaurant


DELIVERY_FEE = Decimal("60.00")
SERVICE_FEE = Decimal("25.00")
TAX_RATE = Decimal("0.13")


class OrderPlacementError(Exception):
    pass


def _parse_food_id(cart_id: str) -> int:
    if cart_id.startswith("food-"):
        return int(cart_id.replace("food-", ""))
    return int(cart_id)


def calculate_cart_totals(cart_items: list, coupon_code: str = "") -> dict:
    """Preview totals for checkout UI (no DB writes)."""
    subtotal = Decimal("0")
    restaurant = None
    for row in cart_items:
        qty = int(row.get("qty", 1))
        if qty < 1:
            continue
        price = Decimal(str(row.get("price", 0)))
        subtotal += price * qty
        if row.get("restaurantId") and restaurant is None:
            restaurant = row.get("restaurantId")

    delivery_fee = DELIVERY_FEE if subtotal else Decimal("0")
    service_fee = SERVICE_FEE if subtotal else Decimal("0")
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01")) if subtotal else Decimal("0")
    discount = Decimal("0")
    promo_msg = ""
    if coupon_code and subtotal:
        promo = validate_coupon(coupon_code, subtotal)
        if promo.get("valid"):
            discount = promo["discount"]
            promo_msg = promo["message"]

    total = subtotal + delivery_fee + service_fee + tax - discount
    if total < 0:
        total = Decimal("0")

    return {
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "service_fee": service_fee,
        "tax": tax,
        "discount": discount,
        "total": total.quantize(Decimal("0.01")),
        "promo_message": promo_msg,
        "item_count": sum(int(r.get("qty", 0)) for r in cart_items),
        "eta_minutes": 35,
    }


@transaction.atomic
def create_order_from_cart(
    user,
    cart_items: list,
    delivery_address: str,
    delivery_contact: str,
    delivery_notes: str = "",
    coupon_code: str = "",
) -> Order:
    if not cart_items:
        raise OrderPlacementError("Your cart is empty.")

    line_items = []
    restaurant = None
    subtotal = Decimal("0")

    for row in cart_items:
        qty = int(row.get("qty", 1))
        if qty < 1:
            continue

        food_id = _parse_food_id(str(row.get("foodId") or row.get("id", "")))
        try:
            food = FoodItem.objects.select_related("restaurant").get(
                pk=food_id,
                is_available=True,
                restaurant__is_active=True,
                restaurant__is_approved=True,
            )
        except (FoodItem.DoesNotExist, ValueError) as exc:
            raise OrderPlacementError(
                f"Menu item is no longer available (id: {food_id})."
            ) from exc

        if restaurant is None:
            restaurant = food.restaurant
        elif food.restaurant_id != restaurant.pk:
            raise OrderPlacementError(
                "Please order from one restaurant at a time."
            )

        unit_price = food.discounted_price
        line_subtotal = unit_price * qty
        subtotal += line_subtotal
        line_items.append((food, qty, unit_price, line_subtotal))

    if not line_items or restaurant is None:
        raise OrderPlacementError("Your cart is empty.")

    min_order = Decimal(str(settings.PLATFORM_MINIMUM_ORDER_VALUE))
    if subtotal < min_order:
        raise OrderPlacementError(
            f"Minimum order is NPR {min_order:.0f}."
        )

    delivery_fee = DELIVERY_FEE
    service_fee = SERVICE_FEE
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    discount = Decimal("0")
    applied_coupon = ""

    if coupon_code:
        promo = validate_coupon(coupon_code, subtotal)
        if not promo.get("valid"):
            raise OrderPlacementError(promo.get("message", "Invalid promo code."))
        discount = promo["discount"]
        applied_coupon = promo["code"]

    total = (subtotal + delivery_fee + service_fee + tax - discount).quantize(Decimal("0.01"))

    order = Order.objects.create(
        user=user,
        restaurant=restaurant,
        status="pending",
        payment_status="pending",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        service_fee=service_fee,
        tax=tax,
        discount=discount,
        coupon_code=applied_coupon,
        total_amount=total,
        delivery_address=delivery_address,
        delivery_contact=delivery_contact,
        delivery_notes=delivery_notes,
        estimated_delivery_minutes=35,
    )

    for food, qty, unit_price, line_subtotal in line_items:
        OrderItem.objects.create(
            order=order,
            food_item=food,
            quantity=qty,
            price=unit_price,
            subtotal=line_subtotal,
        )

    OrderTracking.objects.create(
        order=order,
        status="pending",
        description="Order placed — waiting for restaurant confirmation.",
    )

    return order


def confirm_cod_order(order: Order) -> None:
    """COD orders stay pending until delivery; payment collected on delivery."""
    order.payment_status = "pending"
    order.save(update_fields=["payment_status", "updated_at"])


def cancel_order_by_customer(order: Order, reason: str = "") -> None:
    if not order.can_cancel():
        raise OrderPlacementError(order.cancel_blocked_reason() or "Cannot cancel this order.")

    order.status = "cancelled"
    order.cancelled_at = timezone.now()
    order.cancellation_reason = reason or "Cancelled by customer"
    order.save()

    OrderTracking.objects.create(
        order=order,
        status="cancelled",
        description=order.cancellation_reason,
    )
    try:
        from users.email_dispatcher import dispatch_order_status
        dispatch_order_status(order, "cancelled", order.cancellation_reason)
    except Exception:
        pass


def mark_cod_paid_on_delivery(order: Order) -> None:
    if order.payment_status == "paid":
        return
    order.payment_status = "paid"
    order.save(update_fields=["payment_status", "updated_at"])


def confirm_online_payment_order(order: Order, payment) -> None:
    """Mark order paid after verified gateway payment."""
    from django.utils import timezone

    if order.payment_status == "paid" and order.status != "pending":
        return
    order.payment_status = "paid"
    order.status = "confirmed"
    order.confirmed_at = timezone.now()
    order.save(update_fields=["payment_status", "status", "confirmed_at", "updated_at"])
    OrderTracking.objects.create(
        order=order,
        status="confirmed",
        description=f"Payment received via {payment.payment_method.name}.",
    )
    try:
        from users.email_dispatcher import dispatch_order_status
        dispatch_order_status(order, "confirmed", "Payment received — restaurant notified")
    except Exception:
        pass
