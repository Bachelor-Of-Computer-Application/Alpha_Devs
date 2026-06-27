from django.db import models
from users.models import User
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(models.Model):
    """Subscription plans for restaurants and riders."""
    
    class PlanType(models.TextChoices):
        RESTAURANT_MONTHLY = 'RESTAURANT_MONTHLY', 'Restaurant Monthly'
        RESTAURANT_YEARLY = 'RESTAURANT_YEARLY', 'Restaurant Yearly'
        RIDER_MONTHLY = 'RIDER_MONTHLY', 'Rider Monthly'
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=50, choices=PlanType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text=_('Duration in days'))
    
    # Features (stored as JSON for flexibility)
    features = models.JSONField(default=dict, help_text=_('List of features included'))
    
    # Limits and quotas
    max_menu_items = models.IntegerField(default=100, help_text=_('Maximum menu items allowed'))
    max_orders_per_day = models.IntegerField(default=100, help_text=_('Maximum orders per day'))
    priority_listing = models.BooleanField(default=False, help_text=_('Priority in search results'))
    analytics_access = models.BooleanField(default=True, help_text=_('Access to analytics dashboard'))
    promotional_boosts = models.IntegerField(default=0, help_text=_('Number of promotional boosts per month'))
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text=_('Featured plan for marketing'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - NPR {self.price}"


class PartnerSubscription(models.Model):
    """Active subscription for restaurant partners."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='restaurant_subscriptions'
    )
    
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='restaurant_subscriptions'
    )
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False, help_text=_('Auto-renew subscription'))
    
    # Payment tracking
    payment_status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Restaurant Subscription')
        verbose_name_plural = _('Restaurant Subscriptions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.end_date
    
    def days_remaining(self):
        from django.utils import timezone
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now()).days


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
    restaurant = models.OneToOneField(
        "restaurant.Restaurant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_profile",
    )
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
    partner_code = models.CharField(
        max_length=19,
        unique=True,
        blank=True,
        null=True,
        help_text=_('XXXX-XXXX-XXXX-XXXX — issued on admin approval'),
    )
    subscription = models.ForeignKey(
        PartnerSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='restaurant_partners'
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
        verbose_name = "Restaurant Earnings"
        verbose_name_plural = "Restaurant Earnings"
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.partner.restaurant_name} - {self.period_start}"
