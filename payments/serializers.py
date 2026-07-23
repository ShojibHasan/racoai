from rest_framework import serializers

from orders.models import Order

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "provider", "transaction_id", "status", "created_at", "updated_at"]
        read_only_fields = fields


class InitiateSerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    provider = serializers.ChoiceField(choices=[Payment.STRIPE, Payment.BKASH])

    def validate_order(self, order):
        user = self.context["request"].user
        if order.user_id != user.id:
            raise serializers.ValidationError("Order not found")
        if order.status != Order.PENDING:
            raise serializers.ValidationError("Order is not pending")
        return order
