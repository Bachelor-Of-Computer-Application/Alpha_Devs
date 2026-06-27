from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from api.payment_service import PaymentGatewayService
from orders.models import Order
from orders.services.order_service import confirm_online_payment_order
from payments.esewa import decode_esewa_response
from payments.models import Payment

USER_FRIENDLY_PAYMENT_ERROR = (
    "We couldn't complete your payment. Please try again or choose another method."
)


def _friendly_error(message: str) -> str:
    raw = (message or "").lower()
    technical_markers = (
        "config", "token", "uuid", "traceback", "exception", "error_code",
        "verification_failed", "amount_mismatch", "key ",
    )
    if any(marker in raw for marker in technical_markers):
        return USER_FRIENDLY_PAYMENT_ERROR
    return message or USER_FRIENDLY_PAYMENT_ERROR


def _context_order(request):
    if not request.user.is_authenticated:
        return None
    order_id = request.GET.get("order") or request.session.get("pending_payment_order_id") or request.session.get("last_order_id")
    if not order_id:
        return None
    return Order.objects.filter(pk=order_id, user=request.user).select_related("restaurant").first()


def payment_success(request):
    order_id = request.GET.get("order_id")
    amount = request.GET.get("amount", "0")
    return render(
        request,
        "payments/payment_success.html",
        {"order_id": order_id, "amount": amount},
    )


@login_required
def payment_failed(request):
    order = _context_order(request)
    error_message = _friendly_error(request.GET.get("error", ""))
    try:
        from analytics.services import track_payment
        if order:
            method = ""
            p = Payment.objects.filter(order=order).select_related("payment_method").first()
            if p and p.payment_method_id:
                method = p.payment_method.name
            track_payment(request.user, False, float(order.total_amount), method, order.pk)
    except Exception:
        pass
    return render(
        request,
        "payments/payment_failed.html",
        {"error_message": error_message, "order": order},
    )


@login_required
def payment_cancelled(request):
    order = _context_order(request)
    try:
        from analytics.services import track_checkout_cancelled
        track_checkout_cancelled(request.user, reason="payment_cancelled")
    except Exception:
        pass
    return render(request, "payments/payment_cancelled.html", {"order": order})


@require_http_methods(["GET", "POST"])
def esewa_success(request):
    data_param = request.GET.get("data") or request.POST.get("data", "")
    payload = decode_esewa_response(data_param) if data_param else {}

    ref_id = (
        payload.get("transaction_uuid")
        or request.GET.get("oid")
        or request.GET.get("transaction_uuid", "")
    )
    payment = None

    if ref_id:
        payment = (
            Payment.objects.filter(transaction_id=ref_id)
            .select_related("order")
            .first()
        )

    if payment and payment.order:
        order = payment.order
        status = (payload.get("status") or "").upper()

        if status == "COMPLETE":
            paid_amount = payload.get("total_amount") or payment.amount
            result = PaymentGatewayService.finalize_successful_payment(
                payment,
                transaction_id=ref_id,
                gateway_response=payload or payment.gateway_response,
                paid_amount=paid_amount,
            )
            success = result.get("success", False)
        else:
            payment.status = "processing"
            payment.save(update_fields=["status", "updated_at"])
            result = PaymentGatewayService.process_esewa_payment(payment, ref_id)
            success = result.get("success", False)

        if success:
            confirm_online_payment_order(order, payment)
            try:
                from analytics.services import track_gateway_payment
                track_gateway_payment(request.user, "esewa", "success", float(payment.amount), order.pk)
            except Exception:
                pass
            request.session["last_order_id"] = order.pk
            request.session.pop("pending_payment_order_id", None)
            request.session["clear_cart"] = True
            try:
                from users.email_dispatcher import dispatch_new_order_placed, dispatch_payment_event
                dispatch_new_order_placed(order)
                dispatch_payment_event(payment, "success")
            except Exception:
                pass
            return redirect("order_success")

        request.session["pending_payment_order_id"] = order.pk
        try:
            from analytics.services import track_gateway_payment
            track_gateway_payment(request.user, "esewa", "failed", float(payment.amount), order.pk)
        except Exception:
            pass
        try:
            from users.email_dispatcher import dispatch_payment_event
            dispatch_payment_event(payment, "failed")
        except Exception:
            pass
        messages.error(
            request,
            "We could not verify your eSewa payment. If money was deducted, please contact support with your order number.",
        )
        return redirect("payments:payment_failed")

    messages.error(request, USER_FRIENDLY_PAYMENT_ERROR)
    return redirect("payments:payment_failed")


@require_GET
def esewa_failure(request):
    ref_id = request.GET.get("oid") or request.GET.get("transaction_uuid", "")
    order = None
    if ref_id:
        payment = Payment.objects.filter(transaction_id=ref_id).select_related("order").first()
        if payment:
            if payment.status != "completed":
                payment.status = "cancelled"
                payment.save(update_fields=["status", "updated_at"])
            order = payment.order
            try:
                from users.email_dispatcher import dispatch_payment_event
                dispatch_payment_event(payment, "failed")
            except Exception:
                pass
            if order:
                request.session["pending_payment_order_id"] = order.pk
                request.session["last_order_id"] = order.pk
                try:
                    from analytics.services import track_gateway_payment
                    if request.user.is_authenticated:
                        track_gateway_payment(request.user, "esewa", "failed", float(payment.amount), order.pk)
                except Exception:
                    pass
    messages.info(request, "eSewa payment was cancelled. You can try again when ready.")
    return redirect("payments:payment_cancelled")


@login_required
def khalti_checkout(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user)
    order = payment.order
    if payment.status == "pending":
        payment.status = "initiated"
        payment.save(update_fields=["status", "updated_at"])
    try:
        from analytics.services import track_gateway_payment
        track_gateway_payment(request.user, "khalti", "initiated", float(payment.amount), payment.order_id)
    except Exception:
        pass
    if order:
        request.session["pending_payment_order_id"] = order.pk
        request.session["last_order_id"] = order.pk
    return render(request, "payments/khalti_checkout.html", {
        "payment": payment,
        "order": order,
        "khalti_public_key": getattr(settings, "KHALTI_PUBLIC_KEY", ""),
        "amount_paisa": int(payment.amount * 100),
    })


@login_required
@require_POST
def khalti_verify(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user)
    token = request.POST.get("token")
    if not token:
        messages.error(request, "Payment could not be verified. Please try Khalti again.")
        return redirect("payments:payment_failed")

    result = PaymentGatewayService.process_khalti_payment(payment, token)
    if result.get("success") and payment.order:
        order = payment.order
        confirm_online_payment_order(order, payment)
        try:
            from analytics.services import track_gateway_payment
            track_gateway_payment(request.user, "khalti", "success", float(payment.amount), order.pk)
        except Exception:
            pass
        try:
            from users.email_dispatcher import dispatch_new_order_placed, dispatch_payment_event
            dispatch_new_order_placed(order)
            dispatch_payment_event(payment, "success")
        except Exception:
            pass
        request.session["last_order_id"] = order.pk
        request.session.pop("pending_payment_order_id", None)
        request.session["clear_cart"] = True
        return redirect("order_success")

    if payment.order:
        request.session["pending_payment_order_id"] = payment.order.pk
        request.session["last_order_id"] = payment.order.pk
    try:
        from analytics.services import track_gateway_payment
        track_gateway_payment(request.user, "khalti", "failed", float(payment.amount), payment.order_id)
    except Exception:
        pass
    try:
        from users.email_dispatcher import dispatch_payment_event
        dispatch_payment_event(payment, "failed")
    except Exception:
        pass
    messages.error(request, _friendly_error(result.get("message", "")))
    return redirect("payments:payment_failed")
