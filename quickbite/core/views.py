from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from orders.models import Order
from payments.models import Payment
from restaurant.models import Favorite, FoodItem, Restaurant, Review
from users.models import Address


def _active_restaurants():
    return (
        Restaurant.objects.filter(is_active=True, is_approved=True)
        .select_related("owner")
        .order_by("-is_featured", "-average_rating", "name")
    )


def home(request):
    restaurants = _active_restaurants()
    q = (request.GET.get("q") or "").strip()
    if q:
        restaurants = restaurants.filter(
            Q(name__icontains=q) | Q(location__icontains=q)
        )
        try:
            from analytics.services import track_restaurant_search
            track_restaurant_search(request.user, q, restaurants.count())
        except Exception:
            pass
    restaurants = restaurants[:12]
    return render(
        request,
        "home.html",
        {"restaurants": restaurants, "search_query": q},
    )


def restaurant_list(request):
    restaurants = _active_restaurants()
    return render(
        request,
        "restaurants/restaurants.html",
        {"restaurants": restaurants},
    )


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(
        Restaurant.objects.select_related("owner"),
        pk=pk,
        is_active=True,
        is_approved=True,
    )
    food_items = FoodItem.objects.filter(
        restaurant=restaurant, is_available=True
    ).order_by("-is_featured", "name")
    try:
        from analytics.services import track_restaurant_view
        track_restaurant_view(request.user, restaurant.pk, restaurant.name)
    except Exception:
        pass
    return render(
        request,
        "restaurants/restaurant_detail.html",
        {
            "restaurant": restaurant,
            "food_items": food_items,
        },
    )


@login_required
def profile_dashboard(request):
    tab = request.GET.get("tab", "orders")
    orders = Order.objects.filter(user=request.user).select_related("restaurant").order_by("-created_at")[:20]
    payments = Payment.objects.filter(user=request.user).select_related("payment_method", "order").order_by("-created_at")[:20]
    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-id")
    reviews = Review.objects.filter(user=request.user).select_related("restaurant", "order").order_by("-created_at")[:20]
    favorites = Favorite.objects.filter(user=request.user).select_related("restaurant", "food_item")[:20]
    return render(
        request,
        "profile/profile.html",
        {
            "tab": tab,
            "orders": orders,
            "payments": payments,
            "addresses": addresses,
            "reviews": reviews,
            "favorites": favorites,
        },
    )


def about_page(request):
    return render(request, "about.html")


def services_page(request):
    return render(request, "services.html")


def subscription_plans_page(request):
    return render(request, "subscription_plans.html")


def contact_page(request):
    from django.contrib import messages

    ctx = {}
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("message") or "").strip()
        ctx.update(
            form_name=name,
            form_email=email,
            form_subject=subject,
            form_message=body,
        )
        if not all([name, email, subject, body]):
            messages.error(request, "Please fill in all fields before sending.")
        else:
            try:
                from users import email_service
                email_service._send_email(
                    subject=f"[Contact] {subject}",
                    template="emails/generic_notification.html",
                    context=email_service._base_context(
                        headline=f"Message from {name}",
                        body=f"Email: {email}\n\n{body}",
                    ),
                    to_email=email_service.SUPPORT_EMAIL,
                    email_type="contact_form",
                    rate_limit=False,
                )
            except Exception:
                pass
            messages.success(
                request,
                "Thank you! We received your message and will reply within 24 hours.",
            )
            ctx = {}
    return render(request, "contact.html", ctx)


def faq_page(request):
    return render(request, "faq.html")


def privacy_policy_page(request):
    return render(request, "privacy_policy.html")


def terms_page(request):
    return render(request, "terms.html")


def refund_policy_page(request):
    return render(request, "refund_policy.html")


def careers_page(request):
    return render(request, "careers.html")


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)
