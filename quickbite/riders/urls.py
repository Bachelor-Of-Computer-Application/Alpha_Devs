from django.urls import path

from . import views

app_name = 'riders'

urlpatterns = [
    path('become-a-rider/', views.rider_registration, name='rider_registration'),
    path('rider-dashboard/', views.rider_dashboard, name='rider_dashboard'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('update-location/', views.update_location, name='update_location'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('reject-delivery/<int:delivery_id>/', views.reject_order, name='reject_delivery'),
    path('delivery/<int:delivery_id>/action/', views.delivery_action, name='delivery_action'),
    path('confirm-delivery/<int:order_id>/', views.confirm_delivery_customer, name='confirm_delivery_customer'),
]
