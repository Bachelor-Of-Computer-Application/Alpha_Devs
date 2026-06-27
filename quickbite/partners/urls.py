from django.urls import path

from . import views

app_name = "partners"

urlpatterns = [
    path("partner-with-us/", views.partner_registration, name="partner_registration"),
    path("partner-dashboard/", views.partner_dashboard, name="partner_dashboard"),
    path("dashboard/menu/", views.partner_menu_list, name="partner_menu"),
    path("dashboard/menu/add/", views.partner_menu_add, name="partner_menu_add"),
    path("dashboard/menu/<int:pk>/edit/", views.partner_menu_edit, name="partner_menu_edit"),
    path("dashboard/menu/<int:pk>/delete/", views.partner_menu_delete, name="partner_menu_delete"),
    path("dashboard/orders/", views.partner_orders, name="partner_orders"),
    path("dashboard/orders/<int:pk>/action/", views.partner_order_action, name="partner_order_action"),
    path("dashboard/profile/", views.partner_profile, name="partner_profile"),
    path("dashboard/analytics/", views.partner_analytics, name="partner_analytics"),
]
