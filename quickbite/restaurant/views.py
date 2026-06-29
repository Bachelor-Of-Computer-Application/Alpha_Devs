from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Restaurant, FoodItem, Cuisine, Review, Favorite


def restaurant_list(request):
    """List all restaurants"""
    restaurants = Restaurant.objects.filter(is_active=True)
    cuisines = Cuisine.objects.all()
    
    # Filter by cuisine if provided
    cuisine_id = request.GET.get('cuisine')
    if cuisine_id:
        restaurants = restaurants.filter(cuisines__id=cuisine_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        restaurants = restaurants.filter(name__icontains=search_query)
    
    context = {
        'restaurants': restaurants,
        'cuisines': cuisines,
        'search_query': search_query,
    }
    return render(request, 'restaurant/restaurant_list.html', context)


def restaurant_detail(request, pk):
    """Restaurant detail view"""
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    food_items = restaurant.fooditem_set.filter(is_available=True)
    reviews = restaurant.review_set.all()
    
    context = {
        'restaurant': restaurant,
        'food_items': food_items,
        'reviews': reviews,
    }
    return render(request, 'restaurant/restaurant_detail.html', context)


def restaurant_menu(request, pk):
    """Restaurant menu view"""
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    food_items = restaurant.fooditem_set.filter(is_available=True)
    
    context = {
        'restaurant': restaurant,
        'food_items': food_items,
    }
    return render(request, 'restaurant/restaurant_menu.html', context)


def restaurant_reviews(request, pk):
    """Restaurant reviews view"""
    restaurant = get_object_or_404(Restaurant, pk=pk, is_active=True)
    reviews = restaurant.review_set.all().order_by('-created_at')
    
    context = {
        'restaurant': restaurant,
        'reviews': reviews,
    }
    return render(request, 'restaurant/restaurant_reviews.html', context)


def restaurant_search(request):
    """Search restaurants"""
    query = request.GET.get('q', '')
    restaurants = Restaurant.objects.filter(is_active=True)
    
    if query:
        restaurants = restaurants.filter(name__icontains=query)
    
    context = {
        'restaurants': restaurants,
        'search_query': query,
    }
    return render(request, 'restaurant/restaurant_search.html', context)


def restaurant_by_category(request, category):
    """Filter restaurants by cuisine category"""
    cuisine = get_object_or_404(Cuisine, name__iexact=category)
    restaurants = Restaurant.objects.filter(
        is_active=True,
        cuisines=cuisine
    )
    
    context = {
        'restaurants': restaurants,
        'category': category,
    }
    return render(request, 'restaurant/restaurant_by_category.html', context)
