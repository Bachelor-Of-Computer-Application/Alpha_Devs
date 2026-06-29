"""Coupon validation for checkout."""
from decimal import Decimal

from payments.models import Coupon


def validate_coupon(code: str, subtotal: Decimal) -> dict:
    code = (code or '').strip().upper()
    if not code:
        return {'valid': False, 'message': 'Enter a promo code.'}

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return {'valid': False, 'message': 'Invalid promo code.'}

    if not coupon.is_valid():
        return {'valid': False, 'message': 'This promo code has expired.'}

    if subtotal < coupon.min_order_amount:
        return {
            'valid': False,
            'message': f'Minimum order NPR {coupon.min_order_amount:.0f} required.',
        }

    if coupon.discount_type == 'percentage':
        discount = (subtotal * coupon.discount_value / Decimal('100')).quantize(Decimal('0.01'))
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = min(coupon.discount_value, subtotal)

    return {
        'valid': True,
        'code': coupon.code,
        'discount': discount,
        'message': f'Promo applied — NPR {discount:.0f} off',
    }
