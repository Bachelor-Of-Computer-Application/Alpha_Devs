from django.contrib import admin
from .models import Cuisine, Restaurant, FoodItem, Favorite, Review


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'cuisine_type', 'average_rating', 'total_reviews', 'is_featured', 'is_active']
    list_filter = ['cuisine_type', 'food_category', 'is_veg', 'is_non_veg', 'is_featured', 'is_active']
    search_fields = ['name', 'location', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'food_type', 'category', 'is_available', 'average_rating']
    list_filter = ['food_type', 'category', 'is_available', 'is_featured']
    search_fields = ['name', 'restaurant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'food_item', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'restaurant__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'food_item', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'restaurant__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
