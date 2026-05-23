from django.db import models
from django.contrib.auth.models import User


class Cuisine(models.Model):
    """Cuisine types for categorization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cuisines/', blank=True, null=True)
    
    def __str__(self):
        return self.name


class Restaurant(models.Model):
    CUISINE_TYPE_CHOICES = [
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
    
    FOOD_CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
        ('all', 'All Day'),
    ]
    
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, default='')
    
    # Enhanced fields
    cuisine_type = models.CharField(max_length=50, choices=CUISINE_TYPE_CHOICES, default='other')
    food_category = models.CharField(max_length=20, choices=FOOD_CATEGORY_CHOICES, default='all')
    is_veg = models.BooleanField(default=False)
    is_non_veg = models.BooleanField(default=True)
    
    # Rating and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    
    # Additional info
    description = models.TextField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Images
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    FOOD_TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('both', 'Both'),
    ]
    
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
        ('beverages', 'Beverages'),
        ('desserts', 'Desserts'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Enhanced fields
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES, default='both')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Image
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    
    # Rating
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class Favorite(models.Model):
    """User's favorite restaurants and food items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "restaurant"],
                condition=models.Q(restaurant__isnull=False),
                name="favorite_unique_user_restaurant",
            ),
            models.UniqueConstraint(
                fields=["user", "food_item"],
                condition=models.Q(food_item__isnull=False),
                name="favorite_unique_user_fooditem",
            ),
        ]

    def __str__(self):
        if self.restaurant:
            return f"{self.user.username} - {self.restaurant.name}"
        return f"{self.user.username} - {self.food_item.name}"


class Review(models.Model):
    """Customer reviews for restaurants and food items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True)
    
    rating = models.IntegerField()  # 1-5 stars
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"
