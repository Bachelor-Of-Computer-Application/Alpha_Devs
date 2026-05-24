from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Rider


def rider_registration(request):
    """Delivery rider registration page"""
    if request.method == 'POST':
        # Handle registration form submission
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        emergency_contact = request.POST.get('emergency_contact')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_number = request.POST.get('vehicle_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        # Create user account
        from django.contrib.auth.models import User
        username = phone  # Use phone as username
        user = User.objects.create_user(
            username=username,
            password='default_password123'
        )
        
        # Create rider
        rider = Rider.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            emergency_contact=emergency_contact,
            emergency_contact_name=emergency_contact_name,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            address=address,
            city=city,
            status='pending',
            registration_fee_paid=False
        )
        
        return redirect('/riders/become-a-rider/?success=1')
    
    success = request.GET.get('success')
    return render(request, 'riders/rider_registration.html', {
        'success': success
    })


@login_required
def rider_dashboard(request):
    """Rider dashboard"""
    try:
        rider = Rider.objects.get(user=request.user)
    except Rider.DoesNotExist:
        return redirect('/riders/become-a-rider/')
    
    earnings = rider.riderearnings_set.all()[:5]
    deliveries = rider.delivery_set.all()[:10]
    
    return render(request, 'riders/rider_dashboard.html', {
        'rider': rider,
        'earnings': earnings,
        'deliveries': deliveries
    })
