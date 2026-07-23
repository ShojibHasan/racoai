from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .providers.registry import get_provider
from .serializers import InitiateSerializer, PaymentSerializer
from .services import settle_payment, start_payment


class PaymentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.none()

    def get_queryset(self):
        # A user only sees payments for their own orders
        return Payment.objects.filter(order__user=self.request.user).select_related("order")

    @extend_schema(request=InitiateSerializer, responses=OpenApiTypes.OBJECT)
    @action(detail=False, methods=["post"])
    def initiate(self, request):
        serializer = InitiateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]
        provider = serializer.validated_data["provider"]
        payment, client_data = start_payment(order, provider)
        return Response(
            {"payment": PaymentSerializer(payment).data, "client_data": client_data},
            status=status.HTTP_201_CREATED,
        )


class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        payload = {
            "body": request.body,
            "signature": request.META.get("HTTP_STRIPE_SIGNATURE", ""),
        }
        result = get_provider(Payment.STRIPE).verify(payload)
        settle_payment(result.transaction_id, result.success, result.raw_response)
        return Response({"received": True})


class BkashWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        payment_id = request.data.get("payment_id")
        if not payment_id:
            return Response({"detail": "payment_id required"}, status=status.HTTP_400_BAD_REQUEST)
        result = get_provider(Payment.BKASH).verify({"payment_id": payment_id})
        settle_payment(result.transaction_id, result.success, result.raw_response)
        return Response({"received": True})
