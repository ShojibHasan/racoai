from rest_framework import viewsets

from .models import Category, Product
from .permissions import IsAdminOrReadOnly
from .serializers import CategorySerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()
        status = self.request.query_params.get("status")
        category = self.request.query_params.get("category")
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category_id=category)
        return qs


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # List returns roots only, children come nested via the serializer
        if self.action == "list":
            return Category.objects.filter(parent__isnull=True)
        return Category.objects.all()
