from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class PartnerSubscription(models.Model):
    """Subscription plans for restaurant partners"""
    PLAN_CHOICES = [
        ('monthly', 'Monthly Plan'),
        ('annual', 'Annual Plan'),
        ('special', 'New Year Offer (6 Months)'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - NPR {self.price}"


class RestaurantPartner(models.Model):
    """Restaurant partner registration and management"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    CUISINE_CHOICES = [
        ('nepali', 'Nepali'),
        ('indian', 'Indian'),
        ('chinese', 'Chinese'),
        ('continental', 'Continental'),
        ('italian', 'Italian'),
        ('thai', 'Thai'),
        ('japanese', 'Japanese'),
        ('fast_food', 'Fast Food'),
        ('bakery', 'Bakery'),
        ('cafe', 'Cafe'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=100)
    pan_vat_number = models.CharField(max_length=50, blank=True)
    
    # Document uploads
    citizenship_document = models.FileField(
        upload_to='documents/citizenship/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True
    )
    business_registration = models.FileField(
        upload_to='documents/business/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True
    )
    
    # Restaurant details
    cuisine_type = models.CharField(max_length=50, choices=CUISINE_CHOICES)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Restaurant photos
    restaurant_photo = models.ImageField(
        upload_to='restaurants/photos/',
        blank=True,
        null=True
    )
    
    # Bank/Payment info
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    account_holder_name = models.CharField(max_length=100, blank=True)
    
    # Status and subscription
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subscription = models.ForeignKey(
        PartnerSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.restaurant_name} - {self.status}"


class RestaurantEarnings(models.Model):
    """Track restaurant earnings"""
    partner = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    order_count = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.partner.restaurant_name} - {self.period_start}"
