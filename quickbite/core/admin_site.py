"""Custom QuickBite Django admin site with analytics dashboard."""

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from core.admin_analytics import get_admin_dashboard_context


class QuickBiteAdminSite(admin.AdminSite):
    site_header = "QuickBite Operations"
    site_title = "QuickBite Admin"
    index_title = "Platform overview"
    index_template = "admin/quickbite_index.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "analytics/",
                self.admin_view(self.analytics_dashboard_view),
                name="qb_analytics",
            ),
        ]
        return custom + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(get_admin_dashboard_context())
        return super().index(request, extra_context)

    def analytics_dashboard_view(self, request):
        context = {
            **self.each_context(request),
            "title": "Analytics dashboard",
            **get_admin_dashboard_context(),
        }
        return TemplateResponse(
            request,
            "admin/analytics_dashboard.html",
            context,
        )


admin_site = QuickBiteAdminSite(name="quickbite_admin")
