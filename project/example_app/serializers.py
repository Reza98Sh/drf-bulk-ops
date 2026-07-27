from rest_framework import serializers
from .models import Product

from drf_bulk_ops.serializer import BulkOpsSerializerMixin


class ProductSerializer(BulkOpsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "created_at"]
        read_only_fields = ["created_at"]
