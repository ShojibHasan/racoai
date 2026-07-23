import os

import stripe

from .base import InitiateResult, PaymentProvider, ProviderConfigError, VerifyResult


class StripeProvider(PaymentProvider):
    name = "stripe"

    def _key(self):
        key = os.environ.get("STRIPE_SECRET_KEY")
        if not key:
            raise ProviderConfigError("STRIPE_SECRET_KEY is not set")
        return key

    def initiate(self, order):
        stripe.api_key = self._key()
        # Amount in the smallest currency unit, cents for USD
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="usd",
            metadata={"order_id": order.id},
        )
        return InitiateResult(
            transaction_id=intent.id,
            client_data={"client_secret": intent.client_secret},
            raw_response=dict(intent),
        )

    def verify(self, payload):
        # payload carries the raw body and the Stripe-Signature header
        secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        if not secret:
            raise ProviderConfigError("STRIPE_WEBHOOK_SECRET is not set")
        event = stripe.Webhook.construct_event(
            payload["body"], payload["signature"], secret
        )
        intent = event["data"]["object"]
        success = event["type"] == "payment_intent.succeeded"
        return VerifyResult(
            transaction_id=intent["id"], success=success, raw_response=dict(event)
        )
