from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from users.models import User
from core.decorators import role_required

from analytics.services import track_restaurant_registration
from orders.models import Order
from partners.models import RestaurantPartner, SubscriptionPlan
from restaurant.decorators import restaurant_owner_required
from restaurant.forms import FoodItemForm, RestaurantProfileForm
from restaurant.models import FoodItem
from restaurant.selectors.dashboard import get_dashboard_stats, get_restaurant_for_user
from restaurant.services.menu_service import create_menu_item, delete_menu_item, update_menu_item
from restaurant.services.order_service import assign_rider, update_order_status


def partner_registration(request):
    plans = SubscriptionPlan.objects.filter(is_active=True, plan_type__startswith="RESTAURANT")

    if request.method == "POST":
        from django.contrib.auth import get_user_model
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        User = get_user_model()

        restaurant_name = request.POST.get("restaurant_name")
        owner_name = request.POST.get("owner_name")
        pan_vat = request.POST.get("pan_vat", "")
        cuisine_type = request.POST.get("cuisine_type")
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        phone = request.POST.get("phone")
        email = (request.POST.get("email") or "").strip().lower()
        address = request.POST.get("address")
        city = request.POST.get("city", "Pokhara")
        password = request.POST.get("password")
        subscription_id = request.POST.get("subscription")

        if not password:
            messages.error(request, "Password is required.")
            return render(request, "partners/partner_registration.html", {"plans": plans})

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, " ".join(e.messages))
            return render(request, "partners/partner_registration.html", {"plans": plans})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "partners/partner_registration.html", {"plans": plans})

        username = email.split("@")[0]
        base_username = username
        n = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{n}"
            n += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=User.Role.RESTAURANT,
            first_name=owner_name.split()[0] if owner_name else "",
            last_name=" ".join(owner_name.split()[1:]) if owner_name and len(owner_name.split()) > 1 else "",
        )

        partner = RestaurantPartner.objects.create(
            user=user,
            restaurant_name=restaurant_name,
            owner_name=owner_name,
            pan_vat_number=pan_vat,
            cuisine_type=cuisine_type,
            opening_time=opening_time,
            closing_time=closing_time,
            phone=phone,
            email=email,
            address=address,
            city=city,
            status="pending",
        )

        track_restaurant_registration(user, restaurant_name)

        try:
            from users.email_service import send_partner_welcome_email, send_admin_new_registration_email
            send_partner_welcome_email(user, restaurant_name)
            send_admin_new_registration_email(user, "Restaurant Partner")
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Partner welcome email failed: %s", exc)

        return redirect("/partners/partner-with-us/?success=1")

    return render(
        request,
        "partners/partner_registration.html",
        {
            "subscriptions": plans,
            "plans": plans,
            "success": request.GET.get("success"),
        },
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
def partner_dashboard(request):
    restaurant = get_restaurant_for_user(request.user)
    try:
        partner = RestaurantPartner.objects.get(user=request.user)
    except RestaurantPartner.DoesNotExist:
        return redirect("partners:partner_registration")

    stats = get_dashboard_stats(restaurant) if restaurant else {}
    recent_orders = (
        Order.objects.filter(restaurant=restaurant).order_by("-created_at")[:8]
        if restaurant
        else []
    )

    return render(
        request,
        "partners/partner_dashboard.html",
        {
            "partner": partner,
            "restaurant": restaurant,
            "stats": stats,
            "recent_orders": recent_orders,
        },
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_menu_list(request):
    items = FoodItem.objects.filter(restaurant=request.restaurant).order_by("name")
    return render(
        request,
        "partners/menu_list.html",
        {"items": items, "restaurant": request.restaurant},
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_menu_add(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = request.restaurant
            item.save()
            try:
                from analytics.services import track_food_added, track_menu_updated
                track_food_added(request.user, item.pk, item.name)
                track_menu_updated(request.user, request.restaurant.pk)
            except Exception:
                pass
            messages.success(request, f"Added {item.name} to menu.")
            return redirect("partners:partner_menu")
    else:
        form = FoodItemForm()
    return render(request, "partners/menu_form.html", {"form": form, "action": "Add"})


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_menu_edit(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, restaurant=request.restaurant)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            try:
                from analytics.services import track_food_updated, track_menu_updated
                track_food_updated(request.user, item.pk)
                track_menu_updated(request.user, request.restaurant.pk)
            except Exception:
                pass
            messages.success(request, "Menu item updated.")
            return redirect("partners:partner_menu")
    else:
        form = FoodItemForm(instance=item)
    return render(
        request,
        "partners/menu_form.html",
        {"form": form, "item": item, "action": "Edit"},
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_menu_delete(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, restaurant=request.restaurant)
    if request.method == "POST":
        food_name = item.name
        delete_menu_item(item)
        try:
            from analytics.services import track_food_deleted, track_menu_updated
            track_food_deleted(request.user, item.pk, food_name)
            track_menu_updated(request.user, request.restaurant.pk)
        except Exception:
            pass
        messages.success(request, "Item removed from menu.")
        return redirect("partners:partner_menu")
    return render(request, "partners/menu_confirm_delete.html", {"item": item})


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_orders(request):
    orders = Order.objects.filter(restaurant=request.restaurant).select_related(
        "user", "rider"
    )
    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(
        request,
        "partners/orders.html",
        {"orders": orders.order_by("-created_at"), "restaurant": request.restaurant},
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_order_action(request, pk):
    order = get_object_or_404(Order, pk=pk, restaurant=request.restaurant)
    action = request.POST.get("action")
    try:
        if action in ("confirmed", "preparing", "ready", "cancelled", "picked_up"):
            update_order_status(order, action, request.user)
            try:
                from analytics.services import track_order_accepted, track_order_rejected
                if action == "confirmed":
                    track_order_accepted(request.user, order)
                elif action == "cancelled":
                    track_order_rejected(request.user, order)
            except Exception:
                pass
            messages.success(request, f"Order marked as {action}.")
        elif action == "assign_rider":
            from riders.models import Rider

            rider_id = request.POST.get("rider_id")
            rider = get_object_or_404(Rider, pk=rider_id, status="approved")
            assign_rider(order, rider)
            messages.success(request, f"Assigned rider {rider.full_name}.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("partners:partner_orders")


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_profile(request):
    if request.method == "POST":
        form = RestaurantProfileForm(
            request.POST, request.FILES, instance=request.restaurant
        )
        if form.is_valid():
            form.save()
            try:
                from analytics.services import track_restaurant_profile_updated
                track_restaurant_profile_updated(request.user, request.restaurant.pk)
            except Exception:
                pass
            messages.success(request, "Restaurant profile updated.")
            return redirect("partners:partner_profile")
    else:
        form = RestaurantProfileForm(instance=request.restaurant)
    return render(
        request,
        "partners/partner_profile.html",
        {"form": form, "restaurant": request.restaurant},
    )


@role_required(User.Role.RESTAURANT, login_url="/accounts/login/restaurant/")
@restaurant_owner_required
def partner_analytics(request):
    stats = get_dashboard_stats(request.restaurant)
    return render(
        request,
        "partners/analytics.html",
        {"stats": stats, "restaurant": request.restaurant},
    )
