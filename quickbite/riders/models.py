from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


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
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.rider.full_name} - {self.period_start}"
