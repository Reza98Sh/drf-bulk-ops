# testapp/urls.py
from django.urls import path
from .views import (
    ProductBulkCreateView,
    ProductBulkUpdateView,
    ProductBulkDestroyView,
)

urlpatterns = [
    path('products/bulk/create/', ProductBulkCreateView.as_view(), name='bulk-create'),
    path('products/bulk/update/', ProductBulkUpdateView.as_view(), name='bulk-update'),
    path('products/bulk/delete/', ProductBulkDestroyView.as_view(), name='bulk-delete'),
]
