import logging

from django.db import transaction

from catalog.models import Product
from orders.models import Order

from .models import Payment
from .providers.registry import get_provider

logger = logging.getLogger("payments")


class InsufficientStock(Exception):
    pass


def start_payment(order, provider_name, provider=None):
    if order.status != Order.PENDING:
        raise ValueError("Only a pending order can be paid")
    provider = provider or get_provider(provider_name)
    result = provider.initiate(order)
    payment = Payment.objects.create(
        order=order,
        provider=provider_name,
        transaction_id=result.transaction_id,
        status=Payment.PENDING,
        raw_response=result.raw_response,
    )
    return payment, result.client_data


@transaction.atomic
def settle_payment(transaction_id, success, raw_response):
    payment = Payment.objects.select_for_update().get(transaction_id=transaction_id)
    if payment.is_settled:
        logger.info("Payment %s already settled as %s, skipping", transaction_id, payment.status)
        return payment
    payment.raw_response = raw_response or payment.raw_response
    order = payment.order
    if success:
        try:
            _reduce_stock(order)
        except InsufficientStock as exc:
            logger.warning("Payment %s success but stock short (%s), canceling", transaction_id, exc)
            return _fail(payment, order)
        payment.status = Payment.SUCCESS
        order.status = Order.PAID
    else:
        logger.info("Payment %s reported failed by provider", transaction_id)
        return _fail(payment, order)
    payment.save(update_fields=["status", "raw_response", "updated_at"])
    order.save(update_fields=["status", "updated_at"])
    logger.info("Payment %s settled success, order %s paid", transaction_id, order.pk)
    return payment


def _fail(payment, order):
    payment.status = Payment.FAILED
    order.status = Order.CANCELED
    payment.save(update_fields=["status", "raw_response", "updated_at"])
    order.save(update_fields=["status", "updated_at"])
    return payment


def _reduce_stock(order):
    for item in order.items.all():
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock < item.quantity:
            raise InsufficientStock(product.sku)
        product.stock -= item.quantity
        product.save(update_fields=["stock", "updated_at"])
