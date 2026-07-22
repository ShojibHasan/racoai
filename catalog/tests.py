from decimal import Decimal

from django.db.utils import IntegrityError
from django.test import TestCase

from .models import Category, Product


class ProductModelTests(TestCase):
    def test_defaults(self):
        p = Product.objects.create(name="Mug", sku="MUG-1", price=Decimal("9.99"))
        self.assertEqual(p.stock, 0)
        self.assertEqual(p.status, Product.ACTIVE)

    def test_str(self):
        p = Product.objects.create(name="Mug", sku="MUG-2", price=Decimal("9.99"))
        self.assertEqual(str(p), "Mug (MUG-2)")

    def test_sku_unique(self):
        Product.objects.create(name="A", sku="DUP", price=Decimal("1.00"))
        with self.assertRaises(IntegrityError):
            Product.objects.create(name="B", sku="DUP", price=Decimal("2.00"))


class CategoryModelTests(TestCase):
    def test_parent_relation(self):
        root = Category.objects.create(name="Electronics", slug="electronics")
        child = Category.objects.create(name="Phones", slug="phones", parent=root)
        self.assertEqual(child.parent, root)
        self.assertIn(child, root.children.all())

    def test_slug_unique(self):
        Category.objects.create(name="A", slug="dup")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="B", slug="dup")

    def test_str(self):
        c = Category.objects.create(name="Books", slug="books")
        self.assertEqual(str(c), "Books")
