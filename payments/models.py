from django.db import models

from config.models_base import UUIDModel


class Payment(UUIDModel):
    STRIPE = "stripe"
    BKASH = "bkash"
    PROVIDER_CHOICES = [(STRIPE, "Stripe"), (BKASH, "bKash")]

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    STATUS_CHOICES = [(PENDING, "Pending"), (SUCCESS, "Success"), (FAILED, "Failed")]

    order = models.ForeignKey("orders.Order", related_name="payments", on_delete=models.CASCADE)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.provider}:{self.transaction_id} ({self.status})"

    @property
    def is_settled(self):
        return self.status in (self.SUCCESS, self.FAILED)
