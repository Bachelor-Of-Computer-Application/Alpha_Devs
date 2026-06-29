from django.urls import path

from . import views

urlpatterns = [
    path("", views.order_page, name="order_page"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/", views.order_payment, name="order_payment"),
    path("coupon/apply/", views.apply_coupon, name="apply_coupon"),
    path("success/", views.order_success, name="order_success"),
    path("history/", views.order_history, name="order_history"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("<int:order_id>/review/", views.submit_review, name="submit_review"),
    path("<int:order_id>/reorder/", views.reorder, name="reorder"),
    path("<int:order_id>/invoice/", views.order_invoice, name="order_invoice"),
    path("track/", views.order_tracking, name="order_tracking"),
    path("track/api/<int:order_id>/", views.tracking_api, name="tracking_api"),
]
