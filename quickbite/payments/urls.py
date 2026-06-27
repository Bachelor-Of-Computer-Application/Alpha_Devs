from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),
    path('khalti/<int:payment_id>/', views.khalti_checkout, name='khalti_checkout'),
    path('khalti/<int:payment_id>/verify/', views.khalti_verify, name='khalti_verify'),
]
