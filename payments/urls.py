from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BkashWebhookView, PaymentViewSet, StripeWebhookView

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("payments/webhook/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("payments/webhook/bkash/", BkashWebhookView.as_view(), name="bkash-webhook"),
]
urlpatterns += router.urls
