from django.db import transaction
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from core.decorators import role_required
from orders.models import Order
from riders.models import Delivery, Rider, RiderWallet
from riders.services.delivery_service import (
    accept_delivery,
    available_orders_for_rider,
    create_delivery_offer,
    customer_confirm_delivery,
    get_or_create_wallet,
    mark_delivered,
    mark_in_transit,
    mark_picked_up,
    reject_delivery,
)
from users.models import User

UserModel = get_user_model()


def rider_registration(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = (request.POST.get('email') or '').strip().lower()
        citizenship_id = request.POST.get('citizenship_id', '')
        license_number = request.POST.get('license_number', '')
        emergency_contact = request.POST.get('emergency_contact', phone)
        emergency_contact_name = request.POST.get('emergency_contact_name', full_name)
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number', '')
        address = request.POST.get('address')
        city = request.POST.get('city', 'Pokhara')
        password = request.POST.get('password')

        if not password or not email:
            messages.error(request, 'Email and password are required.')
            return render(request, 'riders/rider_registration.html')

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'riders/rider_registration.html')

        if UserModel.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'riders/rider_registration.html')

        user = UserModel.objects.create_user(email=email, password=password, role=User.Role.RIDER)
        Rider.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            citizenship_id=citizenship_id,
            license_number=license_number,
            emergency_contact=emergency_contact,
            emergency_contact_name=emergency_contact_name,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            address=address,
            city=city,
            status='pending',
        )
        try:
            from users.email_service import send_rider_welcome_email, send_admin_new_registration_email
            send_rider_welcome_email(user, full_name)
            send_admin_new_registration_email(user, "Rider")
        except Exception:
            pass
        try:
            from analytics.services import track_rider_registration
            track_rider_registration(user, full_name)
        except Exception:
            pass
        messages.success(request, 'Application submitted. You will receive your Rider ID by email after approval.')
        return redirect('rider_login')

    return render(request, 'riders/rider_registration.html')


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
def rider_dashboard(request):
    rider = get_object_or_404(Rider, user=request.user)
    wallet = get_or_create_wallet(rider)
    deliveries = Delivery.objects.filter(rider=rider).select_related('order')[:15]
    available = available_orders_for_rider(rider)[:10] if rider.is_available else []

    return render(request, 'riders/rider_dashboard.html', {
        'rider': rider,
        'wallet': wallet,
        'deliveries': deliveries,
        'available_orders': available,
    })


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
@require_POST
def toggle_availability(request):
    rider = get_object_or_404(Rider, user=request.user)
    rider.is_available = not rider.is_available
    rider.save(update_fields=['is_available'])
    messages.success(request, f"Availability: {'On' if rider.is_available else 'Off'}")
    return redirect('riders:rider_dashboard')


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
@require_POST
def accept_order(request, order_id):
    rider = get_object_or_404(Rider, user=request.user)
    if not rider.is_available:
        messages.error(request, 'Turn on availability to accept orders.')
        return redirect('riders:rider_dashboard')

    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order_id)
            if order.status != 'ready':
                messages.error(request, 'This order is no longer available.')
                return redirect('riders:rider_dashboard')
            if order.rider_id:
                messages.error(request, 'Order already assigned to another rider.')
                return redirect('riders:rider_dashboard')
            delivery = create_delivery_offer(order, rider)
            accept_delivery(delivery, rider)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('riders:rider_dashboard')
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect('riders:rider_dashboard')

    try:
        from analytics.services import track_delivery_accepted
        track_delivery_accepted(request.user, order_id, rider.rider_code or "")
    except Exception:
        pass

    messages.success(request, 'Delivery accepted.')
    return redirect('riders:rider_dashboard')


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
@require_POST
def reject_order(request, delivery_id):
    rider = get_object_or_404(Rider, user=request.user)
    delivery = get_object_or_404(Delivery, pk=delivery_id, rider=rider)
    reject_delivery(delivery, rider)
    messages.info(request, 'Delivery rejected.')
    return redirect('riders:rider_dashboard')


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
@require_POST
def delivery_action(request, delivery_id):
    rider = get_object_or_404(Rider, user=request.user)
    delivery = get_object_or_404(Delivery, pk=delivery_id, rider=rider)
    action = request.POST.get('action')
    try:
        if action == 'pickup':
            mark_picked_up(delivery, rider)
            from analytics.services import track_delivery_picked_up
            track_delivery_picked_up(request.user, delivery.order_id)
            messages.success(request, 'Marked picked up.')
        elif action == 'transit':
            mark_in_transit(delivery, rider)
            from analytics.services import track_delivery_in_transit
            track_delivery_in_transit(request.user, delivery.order_id)
            messages.success(request, 'Marked on the way.')
        elif action == 'deliver':
            mark_delivered(delivery, rider)
            from analytics.services import track_delivery_delivered, track_commission_earned
            commission = float(delivery.order.rider_commission or 0)
            track_delivery_delivered(request.user, delivery.order_id, commission)
            if commission:
                track_commission_earned(request.user, commission, delivery.order_id)
            messages.success(request, 'Delivery completed.')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('riders:rider_dashboard')


@role_required(User.Role.RIDER, login_url='/accounts/login/rider/')
@require_POST
def update_location(request):
    rider = get_object_or_404(Rider, user=request.user)
    try:
        lat = float(request.POST.get('latitude', ''))
        lng = float(request.POST.get('longitude', ''))
    except (TypeError, ValueError):
        messages.error(request, 'Invalid location.')
        return redirect('riders:rider_dashboard')
    rider.current_latitude = lat
    rider.current_longitude = lng
    rider.save(update_fields=['current_latitude', 'current_longitude', 'updated_at'])
    messages.success(request, 'Location updated for nearby order sorting.')
    return redirect('riders:rider_dashboard')


@login_required
@require_POST
def confirm_delivery_customer(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    try:
        customer_confirm_delivery(order, request.user)
        from analytics.services import track_customer_confirmed_delivery
        track_customer_confirmed_delivery(request.user, order.pk)
        messages.success(request, 'Thanks for confirming delivery!')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect(f'/orders/track/?order={order.pk}')
