# drf-bulk-ops

Bulk create, update, destroy, and upsert endpoints for [Django REST Framework](https://www.django-rest-framework.org/).

## Features

- Bulk create, update, delete, and upsert API views
- Mixin-based composition for custom viewsets
- Batched Django `bulk_create` / `bulk_update` / `delete`
- Optional atomic transactions
- Optional OpenAPI docs via `drf-spectacular`

## Requirements

- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+

## Installation

```bash
pip install drf-bulk-ops
```

Optional OpenAPI support:

```bash
pip install "drf-bulk-ops[spectacular]"
```

## Setup

Add the app to `INSTALLED_APPS` (recommended; the package has no models):

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "drf_bulk_ops",
]
```

## Quick start

### Serializer

Use `BulkOpsSerializerMixin` so the lookup field can be submitted in update/upsert payloads:

```python
from rest_framework import serializers
from drf_bulk_ops import BulkOpsSerializerMixin
from .models import Product


class ProductSerializer(BulkOpsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock"]
```

### Views

```python
from drf_bulk_ops import (
    BulkCreateView,
    BulkUpdateView,
    BulkDestroyView,
    BulkUpsertView,
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
    serializer_class = ProductSerializer


class ProductBulkUpsertView(BulkUpsertView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### URLs

```python
from django.urls import path
from .views import (
    ProductBulkCreateView,
    ProductBulkUpdateView,
    ProductBulkDestroyView,
    ProductBulkUpsertView,
)

urlpatterns = [
    path("products/bulk/create/", ProductBulkCreateView.as_view()),
    path("products/bulk/update/", ProductBulkUpdateView.as_view()),
    path("products/bulk/delete/", ProductBulkDestroyView.as_view()),
    path("products/bulk/upsert/", ProductBulkUpsertView.as_view()),
]
```

## API examples

**Create** — `POST /products/bulk/create/`

```json
[
  {"name": "Keyboard", "price": "49.99", "stock": 10},
  {"name": "Mouse", "price": "19.99", "stock": 25}
]
```

**Update** — `PUT /products/bulk/update/`

```json
[
  {"id": 1, "name": "Keyboard", "price": "39.99", "stock": 8},
  {"id": 2, "name": "Mouse", "price": "17.99", "stock": 30}
]
```

**Delete** — `DELETE /products/bulk/delete/?ids=1,2`

**Upsert** — `POST /products/bulk/upsert/`

Items with a lookup field are updated; items without one are created:

```json
[
  {"id": 1, "name": "Keyboard", "price": "39.99", "stock": 8},
  {"name": "Headset", "price": "79.99", "stock": 5}
]
```

## View options

| Attribute | Default | Description |
|-----------|---------|-------------|
| `batch_size` | `500` | Batch size for ORM bulk operations |
| `lookup_field` | `"id"` | Field used to match rows for update/delete/upsert |
| `atomic` | `True` | Wrap the operation in `transaction.atomic()` |
| `documentation` | `True` | Auto-extend OpenAPI schema when `drf-spectacular` is installed |

## Development

This repo includes an example Django project under `project/`:

```bash
pip install -e ".[dev]"
cd project
python manage.py migrate
python manage.py runserver
```

Build distributable artifacts:

```bash
python -m build
twine check dist/*
```

## License

MIT
