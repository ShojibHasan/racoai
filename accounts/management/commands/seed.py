import os
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from catalog.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    help = "Seed an admin user and sample categories and products. Safe to run twice."

    def handle(self, *args, **options):
        self._seed_admin()
        categories = self._seed_categories()
        self._seed_products(categories)
        self.stdout.write(self.style.SUCCESS("Seed complete"))

    def _seed_admin(self):
        email = os.environ.get("ADMIN_EMAIL", "admin@racoai.com")
        password = os.environ.get("ADMIN_PASSWORD", "admin12345")
        if User.objects.filter(email=email).exists():
            self.stdout.write(f"Admin {email} already exists")
            return
        User.objects.create_superuser(email=email, password=password, full_name="Admin")
        self.stdout.write(f"Created admin {email}")

    def _seed_categories(self):
        # {slug: parent_slug or None}
        tree = {
            "electronics": None,
            "phones": "electronics",
            "laptops": "electronics",
            "books": None,
        }
        created = {}
        for slug, parent_slug in tree.items():
            parent = created.get(parent_slug)
            cat, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": slug.title(), "parent": parent}
            )
            created[slug] = cat
        return created

    def _seed_products(self, categories):
        samples = [
            ("Pixel Phone", "PHONE-1", "8899.00", 25, "phones"),
            ("Galaxy Phone", "PHONE-2", "7999.00", 40, "phones"),
            ("Ultrabook 14", "LAPTOP-1", "13999.00", 15, "laptops"),
            ("Django for Pros", "BOOK-1", "499.00", 100, "books"),
        ]
        for name, sku, price, stock, cat_slug in samples:
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "price": Decimal(price),
                    "stock": stock,
                    "category": categories[cat_slug],
                },
            )
        self.stdout.write(f"Ensured {len(samples)} sample products")
