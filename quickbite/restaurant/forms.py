from django import forms

from restaurant.models import FoodItem, Restaurant


class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "name",
            "description",
            "phone",
            "email",
            "location",
            "cuisine_type",
            "opening_time",
            "closing_time",
            "delivery_radius_km",
            "latitude",
            "longitude",
            "social_facebook",
            "social_instagram",
            "social_website",
            "logo",
            "banner",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "opening_time": forms.TimeInput(attrs={"type": "time"}),
            "closing_time": forms.TimeInput(attrs={"type": "time"}),
        }


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = [
            "name",
            "description",
            "price",
            "discount_percent",
            "food_type",
            "category",
            "tags",
            "preparation_time_minutes",
            "stock",
            "calories",
            "is_available",
            "is_featured",
            "image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
