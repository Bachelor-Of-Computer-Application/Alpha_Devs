from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Order, OrderItem, OrderTracking, SupportTicket


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)
    autocomplete_fields = ("food_item",)


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ("timestamp",)
    ordering = ("timestamp",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "restaurant",
        "rider",
        "status_badge",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at", "restaurant")
    search_fields = ("order_number", "user__username", "restaurant__name", "delivery_contact")
    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
        "confirmed_at",
        "delivered_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 30
    autocomplete_fields = ("restaurant", "rider")
    inlines = [OrderItemInline, OrderTrackingInline]
    actions = ["mark_delivered", "mark_cancelled"]

    fieldsets = (
        (None, {"fields": ("order_number", "user", "restaurant", "rider", "status", "payment_status")}),
        ("Amounts", {"fields": ("subtotal", "delivery_fee", "tax", "discount", "total_amount")}),
        ("Delivery", {"fields": ("delivery_address", "delivery_contact", "delivery_notes", "estimated_delivery_minutes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "confirmed_at", "delivered_at")}),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "#FFDF00",
            "delivered": "#0E87CC",
            "cancelled": "#EC2459",
        }
        c = colors.get(obj.status, "#0F0F0F")
        return format_html(
            '<span style="background:{};color:#0F0F0F;padding:2px 8px;border-radius:4px;font-size:11px;">{}</span>',
            c,
            obj.get_status_display(),
        )

    @admin.action(description="Mark as delivered")
    def mark_delivered(self, request, queryset):
        from restaurant.services.order_service import update_order_status

        count = 0
        for order in queryset:
            try:
                if order.status == "picked_up":
                    update_order_status(order, "in_transit", request.user, "Admin: in transit")
                    order.refresh_from_db()
                if order.status == "in_transit":
                    update_order_status(order, "delivered", request.user, "Admin: delivered")
                    count += 1
                    try:
                        from analytics.services import track_admin_order_update
                        track_admin_order_update(request.user, order.pk, "delivered")
                    except Exception:
                        pass
                elif order.status not in ("delivered", "cancelled"):
                    self.message_user(
                        request,
                        f"{order.order_number}: cannot deliver from status '{order.status}'.",
                        messages.WARNING,
                    )
            except ValueError as exc:
                self.message_user(request, f"{order.order_number}: {exc}", messages.ERROR)
        if count:
            self.message_user(request, f"Marked {count} order(s) as delivered.", messages.SUCCESS)

    @admin.action(description="Cancel orders")
    def mark_cancelled(self, request, queryset):
        from restaurant.services.order_service import update_order_status

        count = 0
        for order in queryset:
            if order.status == "cancelled":
                continue
            try:
                update_order_status(order, "cancelled", request.user, "Cancelled by admin")
                count += 1
                try:
                    from analytics.services import track_admin_order_update
                    track_admin_order_update(request.user, order.pk, "cancelled")
                except Exception:
                    pass
            except ValueError as exc:
                self.message_user(request, f"{order.order_number}: {exc}", messages.ERROR)
        if count:
            self.message_user(request, f"Cancelled {count} order(s).", messages.SUCCESS)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "food_item", "quantity", "price", "subtotal")
    list_filter = ("order__created_at",)
    search_fields = ("order__order_number", "food_item__name")
    autocomplete_fields = ("order", "food_item")


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "location", "latitude", "longitude", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("order__order_number", "status")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "status", "priority", "created_at")
    list_filter = ("status", "priority", "created_at")
    search_fields = ("user__username", "subject", "description")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    autocomplete_fields = ("order",)
