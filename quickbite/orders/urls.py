from django.urls import path

from . import views

urlpatterns = [
    path("", views.order_page, name="order_page"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.order_success, name="order_success"),
    path("track/", views.order_tracking, name="order_tracking"),
    path("track/api/<int:order_id>/", views.tracking_api, name="tracking_api"),
]
