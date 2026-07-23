from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"
    STATUS_CHOICES = [(PENDING, "Pending"), (PAID, "Paid"), (CANCELED, "Canceled")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"

    def recalculate_total(self, save=True):
        # Deterministic total: sum of every line subtotal
        self.total_amount = sum((item.subtotal for item in self.items.all()), Decimal("0.00"))
        if save:
            self.save(update_fields=["total_amount", "updated_at"])
        return self.total_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # Subtotal is always derived, never trusted from input
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product_id} in order {self.order_id}"
