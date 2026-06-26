from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import FoodItem, Restaurant

SEED = (
    (
        "Himalayan Momo Corner",
        "Thamel, Kathmandu",
        "+977 9801122334",
        (
            ("Steamed Chicken Momo — 10 pc", Decimal("240")),
            ("Buff Jhol Momo", Decimal("280")),
            ("Fried Kothey Momo", Decimal("265")),
            ("Vegetable Momo Combo", Decimal("220")),
        ),
    ),
    (
        "Fire & Slice Pizza Lab",
        "Jhamsikhel, Lalitpur",
        "+977 9805566778",
        (
            ("Margherita — 11 inch", Decimal("549")),
            ("Pepperoni Nepal — 11 inch", Decimal("659")),
            ("Veggie Supreme — 11 inch", Decimal("589")),
            ("Garlic Bread + Dip", Decimal("249")),
            ("Coke 500ml", Decimal("110")),
        ),
    ),
    (
        "Thakali Kitchen Bhanchha",
        "Lazimpat, Kathmandu",
        "+977 9851020304",
        (
            ("Thakali Veg Set", Decimal("420")),
            ("Mutton Curry + Rice + Dal", Decimal("550")),
            ("Chicken Sekuwa", Decimal("380")),
            ("Gundruk Ko Achar Bowl", Decimal("120")),
            ("Local Organic Dahi", Decimal("90")),
        ),
    ),
    (
        "Bhoj Griha Oven",
        "Dillibazar, Kathmandu",
        "+977 9814455667",
        (
            ("Wood-fired Chicken Tikka Pizza", Decimal("695")),
            ("Cream Pasta Alfredo", Decimal("465")),
            ("Caesar Salad", Decimal("385")),
            ("Hot Chocolate Brownie", Decimal("285")),
        ),
    ),
    (
        "Lakeside Oven Pokhara",
        "Lakeside, Pokhara",
        "+977 9866011223",
        (
            ("Breakfast Set — Eggs & Toast", Decimal("395")),
            ("Grilled Trout + Veg", Decimal("680")),
            ("Himalayan Black Coffee", Decimal("185")),
            ("Apple Pie Slice", Decimal("225")),
        ),
    ),
    (
        "Newari Flavours Heritage",
        "Bhaktapur Durbar Marg",
        "+977 9847788990",
        (
            ("Newari Khaja Set — Standard", Decimal("475")),
            ("Bara Wo — 4 pc", Decimal("160")),
            ("Chatamari Chicken", Decimal("220")),
            ("Juju Dhau Bowl", Decimal("150")),
            ("Pau Kwacha — seasonal", Decimal("95")),
        ),
    ),
    (
        "Kathmandu Wok Express",
        "New Road, Kathmandu",
        "+977 9741122335",
        (
            ("Nepali Chowmein — Chicken", Decimal("295")),
            ("Fried Rice — Buff", Decimal("315")),
            ("Manchurian Balls", Decimal("285")),
            ("Wonton Soup", Decimal("220")),
            ("Masala Pepsi", Decimal("85")),
        ),
    ),
    (
        "Baneshwor Biryani House",
        "Baneshwor, Kathmandu",
        "+977 9823344556",
        (
            ("Hyderabadi Chicken Biryani", Decimal("420")),
            ("Mutton Dum Biryani", Decimal("520")),
            ("Chicken 65 Starter", Decimal("295")),
            ("Raita Bowl", Decimal("70")),
            ("Gulab Jamun — 2 pc", Decimal("120")),
        ),
    ),
)


class Command(BaseCommand):
    help = "Seed (or refresh) NPR demo restaurants + menu items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all Restaurant and FoodItem rows before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            FoodItem.objects.all().delete()
            Restaurant.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared Restaurant + FoodItem."))

        if Restaurant.objects.exists():
            self.stdout.write(
                "Restaurants already exist — use --reset to replace. Skipping seed."
            )
            return

        for rest_name, loc, phone, items in SEED:
            r = Restaurant.objects.create(name=rest_name, location=loc, phone=phone)
            for fname, price in items:
                FoodItem.objects.create(restaurant=r, name=fname, price=price)
            self.stdout.write(f"Added {rest_name} ({len(items)} dishes)")
        self.stdout.write(self.style.SUCCESS("QuickBite demo menu seeded."))
