"""Bulk create, update, destroy, and upsert helpers for Django REST Framework."""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("drf-bulk-ops")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

from drf_bulk_ops.exceptions import BulkOperationError, DuplicateKeyError
from drf_bulk_ops.mixins import (
    BulkCreateMixin,
    BulkDestroyMixin,
    BulkUpdateMixin,
    BulkUpsertMixin,
)
from drf_bulk_ops.serializer import BulkOpsSerializerMixin
from drf_bulk_ops.views import (
    BulkCreateDestroyView,
    BulkCreateView,
    BulkDestroyView,
    BulkUpdateView,
    BulkUpsertView,
    GenericBulkAPIView,
)

__all__ = [
    "BulkCreateDestroyView",
    "BulkCreateMixin",
    "BulkCreateView",
    "BulkDestroyMixin",
    "BulkDestroyView",
    "BulkOperationError",
    "BulkOpsSerializerMixin",
    "BulkUpdateMixin",
    "BulkUpdateView",
    "BulkUpsertMixin",
    "BulkUpsertView",
    "DuplicateKeyError",
    "GenericBulkAPIView",
    "__version__",
]
