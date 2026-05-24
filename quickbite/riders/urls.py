from django.urls import path
from . import views

app_name = 'riders'

urlpatterns = [
    path('become-a-rider/', views.rider_registration, name='rider_registration'),
    path('rider-dashboard/', views.rider_dashboard, name='rider_dashboard'),
]
