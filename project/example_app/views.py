from drf_bulk_ops.views import (
    BulkCreateView,
    BulkUpdateView,
    BulkDestroyView,
)
from .models import Product
from .serializers import ProductSerializer


class ProductBulkCreateView(BulkCreateView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductBulkUpdateView(BulkUpdateView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductBulkDestroyView(BulkDestroyView):
    queryset = Product.objects.all()
