from django.contrib import admin, messages

from core.utils.codes import assign_unique_partner_code
from restaurant.models import Restaurant

from .models import SubscriptionPlan, PartnerSubscription, RestaurantEarnings, RestaurantPartner


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "plan_type", "price", "duration_days", "is_active", "is_featured", "created_at")
    list_filter = ("plan_type", "is_active", "is_featured")
    search_fields = ("name",)
    ordering = ("price",)


@admin.register(PartnerSubscription)
class PartnerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "is_active", "payment_status", "created_at")
    list_filter = ("is_active", "payment_status", "plan__plan_type")
    search_fields = ("user__email", "plan__name")
    ordering = ("-created_at",)


@admin.register(RestaurantPartner)
class RestaurantPartnerAdmin(admin.ModelAdmin):
    list_display = (
        "restaurant_name",
        "owner_name",
        "status",
        "partner_code",
        "restaurant_link",
        "subscription",
        "city",
        "created_at",
    )
    list_filter = ("status", "cuisine_type", "subscription", "city", "created_at")
    search_fields = ("restaurant_name", "owner_name", "email", "phone", "pan_vat_number")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    autocomplete_fields = ("restaurant", "subscription")
    actions = ["approve_partners", "reject_partners"]

    fieldsets = (
        (None, {"fields": ("user", "restaurant", "restaurant_name", "owner_name", "status", "partner_code")}),
        ("Legal", {"fields": ("pan_vat_number", "citizenship_document", "business_registration")}),
        ("Details", {"fields": ("cuisine_type", "opening_time", "closing_time", "phone", "email", "address", "city")}),
        ("Media", {"fields": ("restaurant_photo",)}),
        ("Banking", {"fields": ("bank_name", "account_number", "account_holder_name"), "classes": ("collapse",)}),
        ("Subscription", {"fields": ("subscription", "subscription_start", "subscription_end")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Restaurant")
    def restaurant_link(self, obj):
        if obj.restaurant_id:
            return obj.restaurant.name
        return "—"

    @admin.action(description="Approve & create restaurant listing")
    def approve_partners(self, request, queryset):
        from users.email_service import send_partner_approval_email
        from users.models import User

        approved = 0
        for partner in queryset:
            partner.status = "approved"
            if not partner.partner_code:
                partner.partner_code = assign_unique_partner_code(RestaurantPartner)
            if not partner.restaurant_id:
                rest = Restaurant.objects.create(
                    owner=partner.user,
                    name=partner.restaurant_name,
                    location=f"{partner.address}, {partner.city}",
                    phone=partner.phone,
                    email=partner.email,
                    cuisine_type=partner.cuisine_type,
                    opening_time=partner.opening_time,
                    closing_time=partner.closing_time,
                    is_approved=True,
                    is_active=True,
                )
                partner.restaurant = rest
            else:
                partner.restaurant.is_approved = True
                partner.restaurant.is_active = True
                partner.restaurant.save()
            partner.save()
            user = partner.user
            if user.role != User.Role.RESTAURANT:
                user.role = User.Role.RESTAURANT
                user.save(update_fields=["role"])
            try:
                send_partner_approval_email(partner.user, partner)
            except Exception:
                pass
            try:
                from analytics.services import track_restaurant_approved
                track_restaurant_approved(
                    partner.user,
                    partner.partner_code or "",
                    partner.restaurant_name,
                )
                from analytics.services import track_admin_restaurant_approval
                track_admin_restaurant_approval(request.user, partner.pk, "approved")
            except Exception:
                pass
            approved += 1
        self.message_user(request, f"Approved {approved} partner(s). Partner codes emailed.", messages.SUCCESS)

    @admin.action(description="Reject applications")
    def reject_partners(self, request, queryset):
        from users.email_service import send_partner_rejection_email

        count = 0
        for partner in queryset:
            partner.status = "rejected"
            partner.save(update_fields=["status", "updated_at"])
            try:
                send_partner_rejection_email(partner.user, partner)
            except Exception:
                pass
            try:
                from analytics.services import track_restaurant_rejected, track_admin_restaurant_approval
                track_restaurant_rejected(partner.user, partner.restaurant_name)
                track_admin_restaurant_approval(request.user, partner.pk, "rejected")
            except Exception:
                pass
            count += 1
        self.message_user(request, f"Rejected {count} partner(s). Notification emails sent.", messages.WARNING)


@admin.register(RestaurantEarnings)
class RestaurantEarningsAdmin(admin.ModelAdmin):
    list_display = ("partner", "order_count", "total_earnings", "period_start", "period_end")
    list_filter = ("period_start", "period_end")
    search_fields = ("partner__restaurant_name",)
    date_hierarchy = "period_start"
    autocomplete_fields = ("partner",)
