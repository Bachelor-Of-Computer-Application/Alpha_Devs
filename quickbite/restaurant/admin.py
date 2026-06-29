from django.contrib import admin
from django.utils.html import format_html

from .models import Cuisine, Favorite, FoodItem, Restaurant, Review


class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 0
    fields = ("name", "price", "category", "food_type", "is_available", "stock", "is_featured")
    show_change_link = True
    autocomplete_fields = []


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ("name", "description_preview")
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Description")
    def description_preview(self, obj):
        return (obj.description[:60] + "…") if len(obj.description) > 60 else obj.description


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "location",
        "cuisine_type",
        "is_approved",
        "is_featured",
        "is_active",
        "average_rating",
        "order_count",
    )
    list_filter = (
        "is_approved",
        "is_featured",
        "is_active",
        "cuisine_type",
        "food_category",
        "is_veg",
        "created_at",
    )
    search_fields = ("name", "slug", "location", "email", "phone", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "total_reviews")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    autocomplete_fields = []
    inlines = [FoodItemInline]
    actions = ["approve_restaurants", "feature_restaurants"]

    fieldsets = (
        (None, {"fields": ("owner", "name", "slug", "description", "is_approved", "is_active", "is_featured")}),
        ("Contact & location", {"fields": ("location", "phone", "email", "latitude", "longitude", "delivery_radius_km")}),
        ("Operations", {"fields": ("cuisine_type", "food_category", "is_veg", "is_non_veg", "opening_time", "closing_time")}),
        ("Media", {"fields": ("logo", "banner", "image")}),
        ("Social", {"fields": ("social_facebook", "social_instagram", "social_website"), "classes": ("collapse",)}),
        ("Ratings", {"fields": ("average_rating", "total_reviews")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Orders")
    def order_count(self, obj):
        return obj.order_set.count()

    @admin.action(description="Approve selected restaurants")
    def approve_restaurants(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Mark as featured")
    def feature_restaurants(self, request, queryset):
        queryset.update(is_featured=True)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "restaurant",
        "price",
        "discount_percent",
        "category",
        "food_type",
        "stock",
        "is_available",
        "is_featured",
    )
    list_filter = ("category", "food_type", "is_available", "is_featured", "restaurant")
    search_fields = ("name", "restaurant__name", "tags")
    readonly_fields = ("created_at", "updated_at", "average_rating")
    autocomplete_fields = ("restaurant",)
    ordering = ("restaurant__name", "name")
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("restaurant", "name", "description", "image")}),
        ("Pricing", {"fields": ("price", "discount_percent")}),
        ("Details", {"fields": ("category", "food_type", "tags", "preparation_time_minutes", "stock", "calories")}),
        ("Visibility", {"fields": ("is_available", "is_featured", "average_rating")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "food_item", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "restaurant__name")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("restaurant", "food_item")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "food_item", "rating_stars", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "restaurant__name", "comment")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description="Rating")
    def rating_stars(self, obj):
        return format_html('<span style="color:#FFDF00;">{}</span> ★', obj.rating)
