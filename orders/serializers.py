from django.db import transaction
from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "subtotal"]


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product = attrs["product"]
        if product.status != Product.ACTIVE:
            raise serializers.ValidationError(f"Product {product.sku} is not active")
        if attrs["quantity"] > product.stock:
            raise serializers.ValidationError(f"Only {product.stock} in stock for {product.sku}")
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "total_amount", "status", "items", "created_at", "updated_at"]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order needs at least one item")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        order = Order.objects.create(user=user)
        for row in validated_data["items"]:
            product = row["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=row["quantity"],
                price=product.price,
            )
        order.recalculate_total()
        return order
