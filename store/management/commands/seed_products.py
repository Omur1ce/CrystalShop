from django.core.management.base import BaseCommand
from store.models import Product

PRODUCTS = [
    ("Amethyst Point Crystal 50-60mm", 18.00, "Polished amethyst point, approx 50–60mm."),
    ("Rose Quartz Crystal Point", 16.00, "Rose quartz point, gentle pink tone."),
    ("Black Tourmaline Assorted", 12.00, "Assorted black tourmaline pieces for grounding."),
    ("Citrine Crystal 20g", 9.50, "Citrine crystal, approx 20g."),
    ("Aquamarine raw", 22.00, "Raw aquamarine specimen."),
]

class Command(BaseCommand):
    help = "Seed initial products"

    def handle(self, *args, **kwargs):
        for name, price, desc in PRODUCTS:
            Product.objects.update_or_create(
                name=name,
                defaults={"price_gbp": price, "description": desc},
            )
        self.stdout.write(self.style.SUCCESS("Seeded products."))
