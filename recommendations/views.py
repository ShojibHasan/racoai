from drf_spectacular.utils import extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Product
from catalog.serializers import ProductSerializer

from .services import recommend


class RecommendationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=ProductSerializer(many=True))
    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        products = recommend(product)
        return Response(ProductSerializer(products, many=True).data)
