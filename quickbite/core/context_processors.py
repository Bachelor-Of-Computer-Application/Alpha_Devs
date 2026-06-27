"""Shared template context — brand assets & contact info."""

from django.templatetags.static import static

from core.brand import (
    BRAND_ADDRESS,
    BRAND_NAME,
    BUSINESS_HOURS,
    SUPPORT_EMAIL,
    SUPPORT_PHONE,
)


def branding(request):
    logo = static("images/logo-qb.png")
    return {
        "logo_url": logo,
        "logo_path": logo,
        "brand_name": BRAND_NAME,
        "brand_address": BRAND_ADDRESS,
        "support_email": SUPPORT_EMAIL,
        "support_phone": SUPPORT_PHONE,
        "business_hours": BUSINESS_HOURS,
    }
