import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from api.payment_service import PaymentGatewayService
from orders.models import Order
from orders.services.coupon_service import validate_coupon
from orders.services.order_service import (
    OrderPlacementError,
    calculate_cart_totals,
    cancel_order_by_customer,
    confirm_cod_order,
    create_order_from_cart,
)
from payments.esewa import build_esewa_payload
from payments.models import Invoice, Payment
from restaurant.models import FoodItem, Restaurant, Review
from users.models import Address, User


CHECKOUT_SESSION_KEY = "qb_checkout"


def _available_food_items(restaurant_id=None):
    qs = (
        FoodItem.objects.select_related("restaurant")
        .filter(
            is_available=True,
            restaurant__is_active=True,
            restaurant__is_approved=True,
        )
        .order_by("restaurant__name", "name")
    )
    if restaurant_id:
        qs = qs.filter(restaurant_id=restaurant_id)
    return qs


def _get_checkout_session(request):
    return request.session.get(CHECKOUT_SESSION_KEY) or {}


def _save_checkout_session(request, payload):
    request.session[CHECKOUT_SESSION_KEY] = payload
    request.session.modified = True


def _clear_checkout_session(request):
    request.session.pop(CHECKOUT_SESSION_KEY, None)


def order_page(request):
    restaurant_id = request.GET.get("restaurant")
    filter_restaurant = None

    if restaurant_id:
        filter_restaurant = get_object_or_404(
            Restaurant,
            pk=restaurant_id,
            is_active=True,
            is_approved=True,
        )
        from analytics.services import track_restaurant_view

        track_restaurant_view(
            request.user,
            filter_restaurant.pk,
            filter_restaurant.name,
        )

    food_items = _available_food_items(
        filter_restaurant.pk if filter_restaurant else None
    )

    return render(
        request,
        "orders/order_page.html",
        {
            "food_items": food_items,
            "filter_restaurant": filter_restaurant,
        },
    )


def cart(request):
    return render(request, "orders/cart.html")


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    if not request.user.is_email_verified and request.user.role == User.Role.CUSTOMER:
        messages.warning(
            request,
            "Please verify your email before placing an order. "
            "Check your inbox or resend verification from your profile.",
        )
        return redirect("resend_verification")

    if request.method == "GET":
        addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-id")
        try:
            from analytics.services import track_checkout_started
            track_checkout_started(request.user, 0, 0)
        except Exception:
            pass
        return render(request, "orders/checkout.html", {"addresses": addresses})

    cart_raw = request.POST.get("cart_data", "[]")
    try:
        cart_items = json.loads(cart_raw)
    except json.JSONDecodeError:
        messages.error(request, "Invalid cart data. Please add items again.")
        return redirect("cart")

    full_name = request.POST.get("full_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    notes = request.POST.get("notes", "").strip()
    coupon_code = request.POST.get("coupon_code", "").strip()

    if not full_name or not phone or not address:
        messages.error(request, "Please fill in all delivery details.")
        return redirect("checkout")

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    totals = calculate_cart_totals(cart_items, coupon_code)
    if coupon_code and not totals.get("discount"):
        promo = validate_coupon(coupon_code, totals["subtotal"])
        if not promo.get("valid"):
            messages.error(request, promo.get("message", "Invalid promo code."))
            return redirect("checkout")

    restaurant_name = cart_items[0].get("restaurantName", "")
    restaurant_id = cart_items[0].get("restaurantId", "")

    _save_checkout_session(
        request,
        {
            "cart_items": cart_items,
            "full_name": full_name,
            "phone": phone,
            "address": address,
            "notes": notes,
            "coupon_code": coupon_code.upper() if coupon_code else "",
            "totals": {k: str(v) for k, v in totals.items() if k != "promo_message"},
            "restaurant_name": restaurant_name,
            "restaurant_id": restaurant_id,
        },
    )
    return redirect("order_payment")


def _totals_from_order(order):
    return {
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "service_fee": order.service_fee,
        "tax": order.tax,
        "discount": order.discount,
        "total": order.total_amount,
        "eta_minutes": order.estimated_delivery_minutes or 35,
    }


def _checkout_from_order(order):
    return {
        "address": order.delivery_address,
        "phone": order.delivery_contact,
        "restaurant_name": order.restaurant.name,
        "full_name": order.user.get_full_name() or order.user.username,
        "notes": order.delivery_notes,
        "coupon_code": order.coupon_code,
        "retry_order_id": order.pk,
    }


def _unpaid_retry_order(request):
    order_id = request.GET.get("order") or request.session.get("last_order_id")
    if not order_id:
        return None
    return (
        Order.objects.filter(
            pk=order_id,
            user=request.user,
            payment_status="pending",
            status__in=("pending", "confirmed"),
        )
        .select_related("restaurant")
        .first()
    )


@login_required
@require_http_methods(["GET", "POST"])
def order_payment(request):
    checkout_data = _get_checkout_session(request)
    retry_order = None

    if not checkout_data.get("cart_items"):
        retry_order = _unpaid_retry_order(request)
        if retry_order:
            checkout_data = _checkout_from_order(retry_order)
        else:
            messages.error(request, "Your checkout session expired. Please review your cart and try again.")
            return redirect("checkout")

    cart_items = checkout_data.get("cart_items") or []
    totals = (
        _totals_from_order(retry_order)
        if retry_order
        else calculate_cart_totals(cart_items, checkout_data.get("coupon_code", ""))
    )

    if request.method == "GET":
        return render(
            request,
            "orders/payment.html",
            {
                "checkout": checkout_data,
                "totals": totals,
                "retry_order": retry_order,
            },
        )

    payment_method = request.POST.get("payment", "")
    if payment_method not in ("cod", "esewa", "khalti"):
        messages.error(request, "Please select a valid payment method.")
        return redirect("order_payment")

    try:
        from analytics.services import track_payment_method_selected
        track_payment_method_selected(request.user, payment_method)
    except Exception:
        pass

    retry_order_id = request.POST.get("retry_order_id")
    if retry_order_id:
        order = get_object_or_404(
            Order.objects.select_related("restaurant"),
            pk=retry_order_id,
            user=request.user,
        )
        if order.payment_status == "paid":
            return redirect("order_success")
    else:
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        notes = checkout_data.get("notes", "")
        full_name = checkout_data.get("full_name", "")
        delivery_notes = notes or f"Customer: {full_name}"

        try:
            order = create_order_from_cart(
                user=request.user,
                cart_items=cart_items,
                delivery_address=checkout_data["address"],
                delivery_contact=checkout_data["phone"],
                delivery_notes=delivery_notes,
                coupon_code=checkout_data.get("coupon_code", ""),
            )
        except OrderPlacementError as exc:
            messages.error(request, str(exc))
            return redirect("cart")

    existing_payment = (
        Payment.objects.filter(
            order=order,
            status__in=("pending", "initiated", "processing"),
        )
        .select_related("payment_method")
        .first()
    )
    if existing_payment and existing_payment.payment_method.name == payment_method:
        payment = existing_payment
    else:
        try:
            payment = PaymentGatewayService.create_payment(
                user=request.user,
                order=order,
                payment_method_name=payment_method,
                amount=order.total_amount,
            )
        except ValueError as exc:
            if not retry_order_id:
                order.delete()
            messages.error(request, str(exc))
            return redirect("order_payment")

    if payment_method == "cod":
        PaymentGatewayService.process_cod_payment(payment)
        confirm_cod_order(order)
        try:
            from analytics.services import track_cod_completed
            track_cod_completed(request.user, float(order.total_amount), order.pk)
        except Exception:
            pass
        _clear_checkout_session(request)
        request.session["last_order_id"] = order.pk
        request.session["clear_cart"] = True
        try:
            from users.email_dispatcher import dispatch_new_order_placed
            dispatch_new_order_placed(order)
        except Exception:
            pass
        return redirect("order_success")

    PaymentGatewayService.mark_payment_initiated(payment)
    try:
        from analytics.services import track_payment_initiated, track_gateway_payment
        track_payment_initiated(request.user, float(payment.amount), payment_method, order.pk)
        track_gateway_payment(request.user, payment_method, "initiated", float(payment.amount), order.pk)
    except Exception:
        pass
    try:
        from users.email_dispatcher import dispatch_payment_event
        dispatch_payment_event(payment, "initiated")
    except Exception:
        pass
    request.session["last_order_id"] = order.pk
    request.session["pending_payment_order_id"] = order.pk
    if not retry_order_id:
        request.session["clear_cart"] = True
        _clear_checkout_session(request)

    if payment_method == "khalti":
        return redirect("payments:khalti_checkout", payment_id=payment.pk)

    if payment_method == "esewa":
        esewa_data = build_esewa_payload(request, payment, order)
        return render(
            request,
            "orders/esewa_redirect.html",
            {"esewa": esewa_data, "order": order},
        )

    messages.error(request, "Selected payment method is not available.")
    return redirect("order_payment")


@login_required
@require_POST
def apply_coupon(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "message": "Invalid request."}, status=400)

    cart_items = body.get("cart_items", [])
    code = body.get("code", "")
    totals = calculate_cart_totals(cart_items, "")
    result = validate_coupon(code, totals["subtotal"])
    if result.get("valid"):
        result["discount"] = float(result["discount"])
    return JsonResponse(result)


def order_success(request):
    order = None
    payment = None
    order_id = request.session.pop("last_order_id", None) or request.GET.get("order")
    if order_id:
        order = (
            Order.objects.select_related("restaurant")
            .prefetch_related("items__food_item")
            .filter(pk=order_id, user=request.user if request.user.is_authenticated else None)
            .first()
        )
        if order:
            payment = Payment.objects.filter(order=order).select_related("payment_method").first()

    clear_cart = request.session.pop("clear_cart", False)
    return render(
        request,
        "orders/success.html",
        {"order": order, "payment": payment, "clear_cart": clear_cart},
    )


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("restaurant")
        .prefetch_related("items__food_item")
        .order_by("-created_at")
    )
    return render(request, "orders/history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("restaurant", "rider")
        .prefetch_related("items__food_item", "tracking", "reviews"),
        pk=order_id,
        user=request.user,
    )
    payment = Payment.objects.filter(order=order).select_related("payment_method", "invoice").first()
    invoice = getattr(payment, "invoice", None) if payment else None
    can_review = order.status == "delivered" and not order.reviews.filter(user=request.user).exists()
    return render(
        request,
        "orders/detail.html",
        {
            "order": order,
            "payment": payment,
            "invoice": invoice,
            "can_review": can_review,
        },
    )


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    reason = request.POST.get("reason", "").strip() or "Cancelled by customer"
    force = request.POST.get("force") == "1"

    if not order.can_cancel():
        messages.error(request, order.cancel_blocked_reason() or "Cannot cancel this order.")
        return redirect("order_detail", order_id=order.pk)

    if order.cancel_warning() and not force:
        return render(
            request,
            "orders/cancel_confirm.html",
            {"order": order, "reason": reason},
        )

    try:
        cancel_order_by_customer(order, reason)
    except OrderPlacementError as exc:
        messages.error(request, str(exc))
        return redirect("order_detail", order_id=order.pk)

    Payment.objects.filter(order=order, status__in=("pending", "initiated", "processing")).update(
        status="cancelled"
    )
    messages.success(request, "Your order has been cancelled.")
    return redirect("order_history")


@login_required
@require_POST
def submit_review(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user, status="delivered")
    if order.reviews.filter(user=request.user).exists():
        messages.error(request, "You already reviewed this order.")
        return redirect("order_detail", order_id=order.pk)

    restaurant_rating = int(request.POST.get("restaurant_rating", 0))
    rider_rating = int(request.POST.get("rider_rating", 0) or 0)
    comment = request.POST.get("comment", "").strip()

    if restaurant_rating < 1 or restaurant_rating > 5:
        messages.error(request, "Please rate the restaurant (1–5 stars).")
        return redirect("order_detail", order_id=order.pk)

    Review.objects.create(
        user=request.user,
        order=order,
        restaurant=order.restaurant,
        rating=restaurant_rating,
        rider_rating=rider_rating or None,
        comment=comment or "Great experience!",
    )
    try:
        from analytics.services import track_review_submitted
        track_review_submitted(request.user, order.pk, restaurant_rating, rider_rating)
    except Exception:
        pass
    messages.success(request, "Thank you for your review!")
    return redirect("order_detail", order_id=order.pk)


@login_required
def reorder(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__food_item"),
        pk=order_id,
        user=request.user,
    )
    cart_payload = []
    for item in order.items.all():
        food = item.food_item
        if not food.is_available:
            continue
        cart_payload.append(
            {
                "id": f"food-{food.pk}",
                "foodId": str(food.pk),
                "restaurantId": str(order.restaurant_id),
                "restaurantName": order.restaurant.name,
                "name": food.name,
                "price": float(food.discounted_price),
                "image": food.image.url if food.image else "",
                "qty": item.quantity,
            }
        )
    return render(request, "orders/reorder.html", {"order": order, "cart_json": json.dumps(cart_payload)})


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    payment = Payment.objects.filter(order=order).select_related("payment_method").first()
    invoice = Invoice.objects.filter(payment=payment).first() if payment else None
    return render(
        request,
        "orders/invoice.html",
        {"order": order, "payment": payment, "invoice": invoice},
    )


def order_tracking(request):
    order = None
    order_id = request.GET.get("order")
    if order_id and request.user.is_authenticated:
        order = (
            Order.objects.select_related("restaurant", "rider")
            .prefetch_related("tracking")
            .filter(pk=order_id, user=request.user)
            .first()
        )
    elif order_id:
        order = (
            Order.objects.select_related("restaurant", "rider")
            .prefetch_related("tracking")
            .filter(pk=order_id)
            .first()
        )

    map_json = "{}"
    if order:
        map_json = json.dumps(_build_map_payload(order))

    return render(
        request,
        "orders/tracking.html",
        {"order": order, "map_json": map_json, "payment": _order_payment(order) if order else None},
    )


def _order_payment(order):
    from payments.models import Payment
    return Payment.objects.filter(order=order).select_related("payment_method").order_by("-created_at").first()


@require_GET
def tracking_api(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("restaurant", "rider"),
        pk=order_id,
    )
    return JsonResponse(_build_map_payload(order))


def _build_map_payload(order):
    restaurant = order.restaurant
    rider = order.rider
    rest_lat = float(restaurant.latitude) if restaurant.latitude else 27.7172
    rest_lng = float(restaurant.longitude) if restaurant.longitude else 85.3240
    rider_lat = rest_lat + 0.01
    rider_lng = rest_lng + 0.01
    if rider and rider.current_latitude and rider.current_longitude:
        rider_lat = float(rider.current_latitude)
        rider_lng = float(rider.current_longitude)

    dest_lat = float(order.delivery_latitude) if order.delivery_latitude else rest_lat + 0.015
    dest_lng = float(order.delivery_longitude) if order.delivery_longitude else rest_lng + 0.015

    return {
        "order_number": order.order_number,
        "status": order.status,
        "eta_minutes": order.estimated_delivery_minutes or 30,
        "restaurant": {
            "name": restaurant.name,
            "lat": rest_lat,
            "lng": rest_lng,
        },
        "rider": {
            "name": rider.full_name if rider else "Assigning rider…",
            "lat": rider_lat,
            "lng": rider_lng,
        },
        "destination": {"lat": dest_lat, "lng": dest_lng},
        "route": [
            [rest_lat, rest_lng],
            [rider_lat, rider_lng],
            [dest_lat, dest_lng],
        ],
    }
