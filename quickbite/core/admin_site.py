"""Custom QuickBite Django admin site — enterprise command center."""

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from analytics.export import (
    export_analytics_report_xlsx,
    export_orders_csv,
    export_orders_xlsx,
    export_payments_csv,
    export_payments_xlsx,
    export_restaurants_csv,
    export_restaurants_xlsx,
    export_riders_csv,
    export_riders_xlsx,
    export_users_csv,
    export_users_xlsx,
)
from analytics.queries import get_admin_command_center_context, get_full_bi_context
from users.smtp_health import get_email_health_context


class QuickBiteAdminSite(admin.AdminSite):
    site_header = "QuickBite Command Center"
    site_title = "QuickBite Admin"
    index_title = "Operations Intelligence"
    index_template = "admin/quickbite_index.html"

    def each_context(self, request):
        context = super().each_context(request)
        context["is_nav_sidebar_enabled"] = False
        return context

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("search/", self.admin_view(self.global_search_view), name="qb_global_search"),
            path("analytics/", self.admin_view(self.analytics_dashboard_view), name="qb_analytics"),
            path("email-health/", self.admin_view(self.email_health_view), name="qb_email_health"),
            path("export/orders/", self.admin_view(export_orders_csv), name="qb_export_orders"),
            path("export/orders/xlsx/", self.admin_view(export_orders_xlsx), name="qb_export_orders_xlsx"),
            path("export/payments/", self.admin_view(export_payments_csv), name="qb_export_payments"),
            path("export/payments/xlsx/", self.admin_view(export_payments_xlsx), name="qb_export_payments_xlsx"),
            path("export/users/", self.admin_view(export_users_csv), name="qb_export_users"),
            path("export/users/xlsx/", self.admin_view(export_users_xlsx), name="qb_export_users_xlsx"),
            path("export/restaurants/", self.admin_view(export_restaurants_csv), name="qb_export_restaurants"),
            path("export/restaurants/xlsx/", self.admin_view(export_restaurants_xlsx), name="qb_export_restaurants_xlsx"),
            path("export/riders/", self.admin_view(export_riders_csv), name="qb_export_riders"),
            path("export/riders/xlsx/", self.admin_view(export_riders_xlsx), name="qb_export_riders_xlsx"),
            path("export/analytics/", self.admin_view(export_analytics_report_xlsx), name="qb_export_analytics"),
        ]
        return custom + urls

    def index(self, request, extra_context=None):
        from core.admin_console import get_admin_model_directory, get_console_sections
        from core.admin_hubs import (
            get_admin_search_targets,
            get_quick_actions,
        )

        extra_context = extra_context or {}
        extra_context.update(get_admin_command_center_context())
        extra_context.update(get_console_sections())
        extra_context["admin_search_targets"] = get_admin_search_targets()
        extra_context["quick_actions"] = get_quick_actions()
        extra_context["admin_app_list"] = get_admin_model_directory(self, request)
        extra_context["app_list"] = []
        extra_context["available_apps"] = []
        return super().index(request, extra_context)

    def global_search_view(self, request):
        from django.shortcuts import redirect
        from urllib.parse import quote

        from core.admin_hubs import get_admin_search_targets

        q = (request.GET.get("q") or "").strip()
        target = request.GET.get("target", "orders")
        targets = {t["key"]: t["url"] for t in get_admin_search_targets()}
        base = targets.get(target, targets["orders"])
        if not q:
            return redirect(base)
        sep = "&" if "?" in base else "?"
        return redirect(f"{base}{sep}q={quote(q)}")

    def app_index(self, request, app_label, extra_context=None):
        """Send legacy app index pages to the command center hubs."""
        from django.shortcuts import redirect
        from django.urls import reverse

        hub_map = {
            "auth": "users",
            "users": "users",
            "orders": "orders",
            "payments": "payments",
            "restaurant": "restaurants",
            "partners": "partners",
            "riders": "riders",
        }
        anchor = hub_map.get(app_label, "")
        return redirect(reverse("admin:index") + f"#app-{app_label}")

    def analytics_dashboard_view(self, request):
        from core.admin_console import get_console_sections
        from core.admin_hubs import get_admin_search_targets, get_quick_actions

        context = {
            **self.each_context(request),
            "title": "Business Intelligence",
            **get_full_bi_context(),
            **get_console_sections(),
            "admin_search_targets": get_admin_search_targets(),
            "quick_actions": get_quick_actions(),
            "app_list": [],
            "available_apps": [],
        }
        return TemplateResponse(request, "admin/analytics_dashboard.html", context)

    def email_health_view(self, request):
        from users import email_service

        test_result = None
        if request.method == "POST" and request.POST.get("action") == "test_smtp":
            from users.smtp_health import test_smtp_connection
            ok, msg = test_smtp_connection()
            test_result = {"ok": ok, "message": msg}
        elif request.method == "POST" and request.POST.get("action") == "send_test":
            to_email = (request.POST.get("test_email") or request.user.email or "").strip()
            if to_email:
                ok = email_service._send_email(
                    subject="Quick-Bite SMTP test",
                    template="emails/generic_notification.html",
                    context=email_service._base_context(
                        headline="SMTP delivery test",
                        body="If you received this in your Gmail inbox, SMTP is working.",
                    ),
                    to_email=to_email,
                    email_type="smtp_test",
                    rate_limit=False,
                )
                test_result = {
                    "ok": ok,
                    "message": f"Test email {'sent' if ok else 'failed'} to {to_email}.",
                }
            else:
                test_result = {"ok": False, "message": "Enter a recipient email."}

        context = {
            **self.each_context(request),
            "title": "System Health",
            **get_email_health_context(),
            "test_result": test_result,
        }
        return TemplateResponse(request, "admin/email_health.html", context)


admin_site = QuickBiteAdminSite(name="admin")
