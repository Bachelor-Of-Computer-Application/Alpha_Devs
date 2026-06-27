from django.core.management.base import BaseCommand

from payments.models import PaymentMethod


METHODS = (
    ("cod", "Pay with cash when your order is delivered."),
    ("esewa", "Pay securely with your eSewa wallet."),
    ("khalti", "Pay with Khalti digital wallet."),
)


class Command(BaseCommand):
    help = "Create default payment methods (COD, eSewa, Khalti)."

    def handle(self, *args, **options):
        created = 0
        for name, description in METHODS:
            _, was_created = PaymentMethod.objects.update_or_create(
                name=name,
                defaults={"is_active": True, "description": description},
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Payment methods ready ({created} new, {len(METHODS)} total)."
            )
        )
