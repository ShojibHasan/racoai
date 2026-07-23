from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from orders.models import Order

from .models import Payment

User = get_user_model()


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="p@example.com", password="secretpass")
        self.order = Order.objects.create(user=self.user)

    def test_defaults(self):
        pay = Payment.objects.create(order=self.order, provider=Payment.STRIPE, transaction_id="tx1")
        self.assertEqual(pay.status, Payment.PENDING)
        self.assertEqual(pay.raw_response, {})

    def test_transaction_id_unique(self):
        Payment.objects.create(order=self.order, provider=Payment.STRIPE, transaction_id="dup")
        with self.assertRaises(IntegrityError):
            Payment.objects.create(order=self.order, provider=Payment.BKASH, transaction_id="dup")

    def test_str(self):
        pay = Payment.objects.create(order=self.order, provider=Payment.BKASH, transaction_id="tx2")
        self.assertEqual(str(pay), "bkash:tx2 (pending)")

    def test_is_settled(self):
        pay = Payment.objects.create(order=self.order, provider=Payment.STRIPE, transaction_id="tx3")
        self.assertFalse(pay.is_settled)
        pay.status = Payment.SUCCESS
        self.assertTrue(pay.is_settled)
