from django.db import models
from users.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Cuisine(models.Model):
    """Cuisine types for categorization."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="cuisines/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    CUISINE_TYPE_CHOICES = [
        ("nepali", "Nepali"),
        ("indian", "Indian"),
        ("chinese", "Chinese"),
        ("continental", "Continental"),
        ("italian", "Italian"),
        ("thai", "Thai"),
        ("japanese", "Japanese"),
        ("fast_food", "Fast Food"),
        ("bakery", "Bakery"),
        ("cafe", "Cafe"),
        ("other", "Other"),
    ]

    FOOD_CATEGORY_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snacks", "Snacks"),
        ("all", "All Day"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_restaurants",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, default="")

    cuisine_type = models.CharField(
        max_length=50, choices=CUISINE_TYPE_CHOICES, default="other"
    )
    food_category = models.CharField(
        max_length=20, choices=FOOD_CATEGORY_CHOICES, default="all"
    )
    is_veg = models.BooleanField(default=False)
    is_non_veg = models.BooleanField(default=True)

    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)

    description = models.TextField(blank=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)

    logo = models.ImageField(upload_to="restaurants/logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="restaurants/banners/", blank=True, null=True)
    image = models.ImageField(upload_to="restaurants/", blank=True, null=True)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    delivery_radius_km = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.0,
        help_text="Delivery radius in kilometres",
    )

    social_facebook = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_website = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "restaurant"
            slug = base
            n = 1
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class FoodItem(models.Model):
    FOOD_TYPE_CHOICES = [
        ("veg", "Vegetarian"),
        ("non_veg", "Non-Vegetarian"),
        ("both", "Both"),
    ]

    CATEGORY_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snacks", "Snacks"),
        ("beverages", "Beverages"),
        ("desserts", "Desserts"),
    ]

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menu_items"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage off (0–100)",
    )

    food_type = models.CharField(
        max_length=10, choices=FOOD_TYPE_CHOICES, default="both"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    tags = models.CharField(
        max_length=255, blank=True,
        help_text="Comma-separated tags, e.g. spicy,bestseller",
    )
    preparation_time_minutes = models.PositiveIntegerField(default=15)
    stock = models.PositiveIntegerField(default=100)
    calories = models.PositiveIntegerField(null=True, blank=True)

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    image = models.ImageField(upload_to="food_items/", blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    @property
    def discounted_price(self):
        if self.discount_percent:
            return self.price * (1 - self.discount_percent / 100)
        return self.price


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, null=True, blank=True
    )
    food_item = models.ForeignKey(
        FoodItem, on_delete=models.CASCADE, null=True, blank=True
    )
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, null=True, blank=True
    )
    food_item = models.ForeignKey(
        FoodItem, on_delete=models.CASCADE, null=True, blank=True
    )
    rating = models.IntegerField()
    rider_rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"


class FoodVariant(models.Model):
    """Food item variants (e.g., size, spice level)."""
    
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    
    name = models.CharField(max_length=100, help_text=_('Variant name, e.g., Small, Medium, Large'))
    price_adjustment = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_('Price adjustment from base price')
    )
    is_available = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Food Variant')
        verbose_name_plural = _('Food Variants')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.food_item.name} - {self.name}"


class FoodAddon(models.Model):
    """Food item addons (e.g., extra cheese, toppings)."""
    
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='addons'
    )
    
    name = models.CharField(max_length=100, help_text=_('Addon name, e.g., Extra Cheese'))
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Food Addon')
        verbose_name_plural = _('Food Addons')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.food_item.name} - {self.name}"
