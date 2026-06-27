from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("restaurants/", views.restaurant_list, name="restaurants"),
    path("restaurants/<int:pk>/", views.restaurant_detail, name="restaurant_detail"),
    path("profile/", views.profile_dashboard, name="profile"),
    path("about/", views.about_page, name="about"),
    path("services/", views.services_page, name="services"),
    path("contact/", views.contact_page, name="contact"),
    path("subscription-plans/", views.subscription_plans_page, name="subscription_plans"),
    path("faq/", views.faq_page, name="faq"),
    path("privacy-policy/", views.privacy_policy_page, name="privacy_policy"),
    path("terms/", views.terms_page, name="terms"),
    path("refund-policy/", views.refund_policy_page, name="refund_policy"),
    path("careers/", views.careers_page, name="careers"),
]
