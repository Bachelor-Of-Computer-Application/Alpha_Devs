from django.core.management.base import BaseCommand
from partners.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create initial subscription plans for QuickBite'

    def handle(self, *args, **options):
        # Check if plans already exist
        try:
            if SubscriptionPlan.objects.exists():
                self.stdout.write(self.style.WARNING('Subscription plans already exist. Skipping creation.'))
                return
        except:
            # Table doesn't exist yet, continue with creation
            pass

        # Restaurant Monthly Plan (NPR 10,000/month)
        monthly_plan = SubscriptionPlan.objects.create(
            name='Restaurant Monthly Plan',
            plan_type='RESTAURANT_MONTHLY',
            price=10000.00,
            duration_days=30,
            features={
                'unlimited_menu_uploads': True,
                'analytics_dashboard': True,
                'priority_listing': False,
                'order_management': True,
                'customer_insights': True
            },
            max_menu_items=100,
            max_orders_per_day=100,
            priority_listing=False,
            analytics_access=True,
            promotional_boosts=0,
            is_active=True,
            is_featured=False
        )

        # Restaurant Yearly Plan (NPR 100,000/year - 2 months free)
        yearly_plan = SubscriptionPlan.objects.create(
            name='Restaurant Yearly Plan',
            plan_type='RESTAURANT_YEARLY',
            price=100000.00,
            duration_days=365,
            features={
                'unlimited_menu_uploads': True,
                'analytics_dashboard': True,
                'priority_listing': True,
                'order_management': True,
                'customer_insights': True,
                'promotional_boosts': 5,
                'featured_placement': True
            },
            max_menu_items=500,
            max_orders_per_day=500,
            priority_listing=True,
            analytics_access=True,
            promotional_boosts=5,
            is_active=True,
            is_featured=True
        )

        # Rider Monthly Plan (NPR 1,000/month)
        rider_plan = SubscriptionPlan.objects.create(
            name='Rider Monthly Plan',
            plan_type='RIDER_MONTHLY',
            price=1000.00,
            duration_days=30,
            features={
                'delivery_access': True,
                'rider_dashboard': True,
                'earnings_analytics': True,
                'priority_delivery_allocation': True
            },
            max_menu_items=0,
            max_orders_per_day=50,
            priority_listing=False,
            analytics_access=True,
            promotional_boosts=0,
            is_active=True,
            is_featured=False
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created 3 subscription plans:'))
        self.stdout.write(f'  - {monthly_plan.name} (NPR {monthly_plan.price}/month)')
        self.stdout.write(f'  - {yearly_plan.name} (NPR {yearly_plan.price}/year)')
        self.stdout.write(f'  - {rider_plan.name} (NPR {rider_plan.price}/month)')
