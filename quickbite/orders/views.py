import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from orders.models import Order
from restaurant.models import FoodItem, Restaurant


def order_page(request):
    restaurant_id = request.GET.get("restaurant")
    food_items = FoodItem.objects.select_related("restaurant").all().order_by(
        "restaurant__name",
        "name",
    )
    filter_restaurant = None

    if restaurant_id:
        filter_restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        food_items = food_items.filter(restaurant_id=filter_restaurant.pk)
        from analytics.services import track_restaurant_view

        track_restaurant_view(
            request.user,
            filter_restaurant.pk,
            filter_restaurant.name,
        )

    return render(
        request,
        "orders/order_page.html",
        {
            "food_items": food_items,
            "filter_restaurant": filter_restaurant,
        },
    )


def cart(request):
    return render(request, "orders/cart.html")


@login_required
def checkout(request):
    return render(request, "orders/checkout.html")


def order_success(request):
    return render(request, "orders/success.html")


def order_tracking(request):
    """Live delivery map (Leaflet + OpenStreetMap)."""
    order = None
    order_id = request.GET.get("order")
    if order_id:
        order = (
            Order.objects.select_related("restaurant", "rider")
            .filter(pk=order_id)
            .first()
        )

    map_json = "{}"
    if order:
        map_json = json.dumps(_build_map_payload(order))

    return render(
        request,
        "orders/tracking.html",
        {"order": order, "map_json": map_json},
    )


@require_GET
def tracking_api(request, order_id):
    """JSON endpoint for polling rider / delivery position."""
    order = get_object_or_404(
        Order.objects.select_related("restaurant", "rider"),
        pk=order_id,
    )
    return JsonResponse(_build_map_payload(order))


def _build_map_payload(order):
    restaurant = order.restaurant
    rider = order.rider
    rest_lat = float(restaurant.latitude) if restaurant.latitude else 27.7172
    rest_lng = float(restaurant.longitude) if restaurant.longitude else 85.3240
    rider_lat = rest_lat + 0.01
    rider_lng = rest_lng + 0.01
    if rider and rider.current_latitude and rider.current_longitude:
        rider_lat = float(rider.current_latitude)
        rider_lng = float(rider.current_longitude)

    dest_lat = rest_lat + 0.015
    dest_lng = rest_lng + 0.015

    return {
        "order_number": order.order_number,
        "status": order.status,
        "eta_minutes": order.estimated_delivery_minutes or 30,
        "restaurant": {
            "name": restaurant.name,
            "lat": rest_lat,
            "lng": rest_lng,
        },
        "rider": {
            "name": rider.full_name if rider else "Assigning rider…",
            "lat": rider_lat,
            "lng": rider_lng,
        },
        "destination": {"lat": dest_lat, "lng": dest_lng},
        "route": [
            [rest_lat, rest_lng],
            [rider_lat, rider_lng],
            [dest_lat, dest_lng],
        ],
    }
