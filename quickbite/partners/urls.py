from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('partner-with-us/', views.partner_registration, name='partner_registration'),
    path('partner-dashboard/', views.partner_dashboard, name='partner_dashboard'),
]
