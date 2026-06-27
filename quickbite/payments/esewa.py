"""eSewa payment form helpers (v2 API)."""
import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse


def _merchant_credentials():
    merchant = getattr(settings, "ESEWA_MERCHANT_CODE", "") or ""
    secret = getattr(settings, "ESEWA_SECRET_KEY", "") or ""
    if not merchant or not secret:
        # Official eSewa sandbox credentials for development
        merchant = "EPAYTEST"
        secret = "8gBm/:&EnhH.1/q"
    return merchant, secret


def esewa_form_url():
    if settings.DEBUG:
        return "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
    return "https://epay.esewa.com.np/api/epay/main/v2/form"


def build_esewa_payload(request, payment, order) -> dict:
    merchant, secret = _merchant_credentials()
    transaction_uuid = f"QB-{payment.id}-{uuid.uuid4().hex[:8]}"

    total = Decimal(str(payment.amount)).quantize(Decimal("0.01"))
    amount = total
    tax_amount = Decimal("0")
    service_charge = Decimal("0")
    delivery_charge = Decimal("0")

    signed_field_names = "total_amount,transaction_uuid,product_code"
    message = (
        f"total_amount={total},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={merchant}"
    )
    signature = base64.b64encode(
        hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")

    success_url = request.build_absolute_uri(reverse("payments:esewa_success"))
    failure_url = request.build_absolute_uri(reverse("payments:esewa_failure"))

    payment.transaction_id = transaction_uuid
    payment.status = "initiated"
    payment.gateway_response = {"transaction_uuid": transaction_uuid}
    payment.save(update_fields=["transaction_id", "status", "gateway_response", "updated_at"])

    return {
        "amount": str(amount),
        "tax_amount": str(tax_amount),
        "total_amount": str(total),
        "transaction_uuid": transaction_uuid,
        "product_code": merchant,
        "product_service_charge": str(service_charge),
        "product_delivery_charge": str(delivery_charge),
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": signed_field_names,
        "signature": signature,
        "form_action": esewa_form_url(),
    }


def decode_esewa_response(data_param: str) -> dict:
    """Decode base64 `data` query param returned by eSewa."""
    try:
        raw = base64.b64decode(data_param)
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, ValueError):
        return {}
