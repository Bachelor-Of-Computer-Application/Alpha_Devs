from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PartnerSubscription, RestaurantPartner


def partner_registration(request):
    """Restaurant partner registration page"""
    subscriptions = PartnerSubscription.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Handle registration form submission
        restaurant_name = request.POST.get('restaurant_name')
        owner_name = request.POST.get('owner_name')
        pan_vat = request.POST.get('pan_vat')
        cuisine_type = request.POST.get('cuisine_type')
        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        subscription_id = request.POST.get('subscription')
        
        # Create user account (simplified - in production, you'd want proper form validation)
        from django.contrib.auth.models import User
        username = email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=email,
            password='default_password123'  # Should be changed on first login
        )
        
        # Create restaurant partner
        subscription = PartnerSubscription.objects.get(id=subscription_id) if subscription_id else None
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
            subscription=subscription,
            status='pending'
        )
        
        return redirect('/partners/partner-with-us/?success=1')
    
    success = request.GET.get('success')
    return render(request, 'partners/partner_registration.html', {
        'subscriptions': subscriptions,
        'success': success
    })


@login_required
def partner_dashboard(request):
    """Restaurant partner dashboard"""
    try:
        partner = RestaurantPartner.objects.get(user=request.user)
    except RestaurantPartner.DoesNotExist:
        return redirect('/partners/partner-with-us/')
    
    earnings = partner.restaurantearnings_set.all()[:5]
    
    return render(request, 'partners/partner_dashboard.html', {
        'partner': partner,
        'earnings': earnings
    })
