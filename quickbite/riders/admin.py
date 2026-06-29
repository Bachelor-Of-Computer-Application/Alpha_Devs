from django.contrib import admin, messages

from core.utils.codes import assign_unique_rider_code

from .models import Delivery, Rider, RiderEarnings, RiderWallet


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'rider_code', 'phone', 'vehicle_type', 'status',
        'is_available', 'registration_fee_paid',
    ]
    list_filter = ['status', 'vehicle_type', 'is_available', 'registration_fee_paid']
    search_fields = ['full_name', 'phone', 'vehicle_number', 'rider_code']
    readonly_fields = ['created_at', 'updated_at', 'rider_code']
    actions = ['approve_riders', 'reject_riders']

    @admin.action(description='Approve riders & issue Rider ID')
    def approve_riders(self, request, queryset):
        from users.email_service import send_rider_approval_email

        count = 0
        from users.models import User

        for rider in queryset:
            rider.status = 'approved'
            if not rider.rider_code:
                rider.rider_code = assign_unique_rider_code(Rider)
            rider.save()
            user = rider.user
            if user.role != User.Role.RIDER:
                user.role = User.Role.RIDER
            if not user.is_active:
                user.is_active = True
            user.save(update_fields=['role', 'is_active'])
            RiderWallet.objects.get_or_create(rider=rider)
            try:
                send_rider_approval_email(rider.user, rider)
            except Exception:
                pass
            try:
                from analytics.services import track_rider_approved, track_admin_rider_approval
                track_rider_approved(rider.user, rider.rider_code or "")
                track_admin_rider_approval(request.user, rider.pk, "approved")
            except Exception:
                pass
            count += 1
        self.message_user(request, f'Approved {count} rider(s). Rider IDs emailed.', messages.SUCCESS)

    @admin.action(description='Reject riders')
    def reject_riders(self, request, queryset):
        from users.email_service import send_rider_rejection_email

        count = 0
        for rider in queryset:
            rider.status = 'rejected'
            rider.save(update_fields=['status', 'updated_at'])
            try:
                send_rider_rejection_email(rider.user, rider)
            except Exception:
                pass
            try:
                from analytics.services import track_rider_rejected, track_admin_rider_approval
                track_rider_rejected(rider.user)
                track_admin_rider_approval(request.user, rider.pk, "rejected")
            except Exception:
                pass
            count += 1
        self.message_user(request, f'Rejected {count} rider(s). Notification emails sent.', messages.WARNING)


@admin.register(RiderWallet)
class RiderWalletAdmin(admin.ModelAdmin):
    list_display = ['rider', 'total_earnings', 'withdrawable_balance', 'delivery_count']
    search_fields = ['rider__full_name']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'rider', 'order', 'status', 'rejected', 'created_at']
    list_filter = ['status', 'rejected', 'created_at']
    search_fields = ['rider__full_name', 'delivery_address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RiderEarnings)
class RiderEarningsAdmin(admin.ModelAdmin):
    list_display = ['rider', 'delivery_count', 'total_earnings', 'period_start', 'period_end']
    list_filter = ['period_start', 'period_end']
    search_fields = ['rider__full_name']
