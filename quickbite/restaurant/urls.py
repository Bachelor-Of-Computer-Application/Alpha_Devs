from django.urls import path

from . import views_redirect as views

app_name = 'restaurant'

urlpatterns = [
    path('', views.redirect_restaurants),
    path('<int:pk>/', views.redirect_restaurant_detail),
    path('<int:pk>/menu/', views.redirect_restaurant_detail),
    path('<int:pk>/reviews/', views.redirect_restaurant_detail),
    path('search/', views.redirect_restaurants),
    path('category/<str:category>/', views.redirect_restaurants),
]
