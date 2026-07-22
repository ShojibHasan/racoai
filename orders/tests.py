from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Product

from .models import Order, OrderItem

User = get_user_model()


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="o@example.com", password="secretpass")
        self.p1 = Product.objects.create(name="A", sku="A1", price=Decimal("10.00"), stock=5)
        self.p2 = Product.objects.create(name="B", sku="B1", price=Decimal("2.50"), stock=5)

    def test_defaults(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.status, Order.PENDING)
        self.assertEqual(order.total_amount, Decimal("0.00"))

    def test_subtotal_auto_computed(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem.objects.create(order=order, product=self.p1, quantity=3, price=self.p1.price)
        self.assertEqual(item.subtotal, Decimal("30.00"))

    def test_recalculate_total(self):
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, product=self.p1, quantity=3, price=self.p1.price)
        OrderItem.objects.create(order=order, product=self.p2, quantity=2, price=self.p2.price)
        order.recalculate_total()
        self.assertEqual(order.total_amount, Decimal("35.00"))

    def test_str(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(str(order), f"Order #{order.pk} (pending)")
