import uuid

from django.db import models
from users.models import User
from restaurant.models import FoodItem, Restaurant


def generate_order_number():
    return f"QB-{uuid.uuid4().hex[:12].upper()}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rider = models.ForeignKey(
        "riders.Rider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True, default=generate_order_number)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Delivery details
    delivery_address = models.TextField(default='')
    delivery_contact = models.CharField(max_length=20, default='')
    delivery_notes = models.TextField(blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    estimated_delivery_minutes = models.PositiveIntegerField(null=True, blank=True)

    # Fees & commissions
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rider_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Delivery confirmation
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    rider_confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def can_cancel(self):
        return self.status in ('pending', 'confirmed', 'preparing', 'ready')

    def cancel_warning(self):
        if self.status in ('confirmed', 'preparing', 'ready'):
            return 'Restaurant has already accepted this order. Cancellation may still be possible.'
        return ''

    def cancel_blocked_reason(self):
        if self.status == 'cancelled':
            return 'This order is already cancelled.'
        if self.status in ('picked_up', 'in_transit', 'delivered'):
            return 'Your order is already with the rider or delivered and cannot be cancelled online.'
        if self.status == 'failed':
            return 'This order has failed and cannot be cancelled.'
        return 'This order can no longer be cancelled online. Contact support.'

    def timeline_index(self):
        if self.status == 'cancelled':
            return -1
        flow = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'in_transit', 'delivered']
        return flow.index(self.status) if self.status in flow else 0

    TIMELINE = [
        ('pending', 'Order Placed'),
        ('confirmed', 'Restaurant Accepted'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'On The Way'),
        ('delivered', 'Delivered'),
    ]

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.food_item.name} x {self.quantity}"


class OrderTracking(models.Model):
    """Order tracking timeline"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=50)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class SupportTicket(models.Model):
    """Customer support requests"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Admin response
    admin_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.id} - {self.subject}"
