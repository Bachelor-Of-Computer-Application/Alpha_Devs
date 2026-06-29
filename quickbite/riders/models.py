from django.db import models
from users.models import User
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


class Rider(models.Model):
    """Delivery rider registration and management"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    VEHICLE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('scooter', 'Scooter'),
        ('bicycle', 'Bicycle'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    citizenship_id = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    emergency_contact = models.CharField(max_length=20)
    emergency_contact_name = models.CharField(max_length=100)
    
    # Document uploads
    citizenship_document = models.FileField(
        upload_to='documents/rider_citizenship/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True
    )
    driving_license = models.FileField(
        upload_to='documents/rider_license/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True
    )
    profile_photo = models.ImageField(
        upload_to='riders/photos/',
        blank=True,
        null=True
    )
    
    # Vehicle details
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    vehicle_number = models.CharField(max_length=20)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Status and availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rider_code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        help_text=_('6-character ID issued on admin approval'),
    )
    is_available = models.BooleanField(default=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Registration fee
    registration_fee_paid = models.BooleanField(default=False)
    registration_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    
    # Earnings
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"


class Delivery(models.Model):
    """Delivery assignments for riders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejected = models.BooleanField(default=False)
    
    # Delivery details
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    delivery_contact = models.CharField(max_length=20)
    
    # Timestamps
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery proof
    delivery_photo = models.ImageField(
        upload_to='deliveries/proof/',
        blank=True,
        null=True
    )
    delivery_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery #{self.id} - {self.status}"


class RiderEarnings(models.Model):
    """Track rider earnings"""
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    delivery_count = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rider Earnings"
        verbose_name_plural = "Rider Earnings"
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.rider.full_name} - {self.period_start}"


class RiderWallet(models.Model):
    """Rider earnings wallet — tracks delivery fees and commissions."""

    rider = models.OneToOneField(Rider, on_delete=models.CASCADE, related_name='wallet')
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    withdrawable_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet — {self.rider.full_name}"


class RiderSubscription(models.Model):
    """Active subscription for riders."""
    
    rider = models.OneToOneField(
        Rider,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    
    plan = models.ForeignKey(
        'partners.SubscriptionPlan',
        on_delete=models.PROTECT,
        related_name='rider_subscriptions',
        limit_choices_to={'plan_type': 'RIDER_MONTHLY'}
    )
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False, help_text=_('Auto-renew subscription'))
    
    # Payment tracking
    payment_status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Benefits
    priority_delivery_allocation = models.BooleanField(default=True, help_text=_('Get priority for delivery assignments'))
    earnings_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, help_text=_('Earnings multiplier (e.g., 1.1 for 10% bonus)'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Rider Subscription')
        verbose_name_plural = _('Rider Subscriptions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rider.full_name} - {self.plan.name}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.end_date
    
    def days_remaining(self):
        from django.utils import timezone
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now()).days
