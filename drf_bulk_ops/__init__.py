"""Bulk create, update, destroy, and upsert helpers for Django REST Framework."""

from __future__ import annotations

from typing import Any

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("drf-bulk-ops")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.1"

# Keep this module free of DRF imports so Django can load the app from
# INSTALLED_APPS before the app registry is ready.
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

_EXPORTS = {
    "BulkCreateDestroyView": ("drf_bulk_ops.views", "BulkCreateDestroyView"),
    "BulkCreateMixin": ("drf_bulk_ops.mixins", "BulkCreateMixin"),
    "BulkCreateView": ("drf_bulk_ops.views", "BulkCreateView"),
    "BulkDestroyMixin": ("drf_bulk_ops.mixins", "BulkDestroyMixin"),
    "BulkDestroyView": ("drf_bulk_ops.views", "BulkDestroyView"),
    "BulkOperationError": ("drf_bulk_ops.exceptions", "BulkOperationError"),
    "BulkOpsSerializerMixin": ("drf_bulk_ops.serializer", "BulkOpsSerializerMixin"),
    "BulkUpdateMixin": ("drf_bulk_ops.mixins", "BulkUpdateMixin"),
    "BulkUpdateView": ("drf_bulk_ops.views", "BulkUpdateView"),
    "BulkUpsertMixin": ("drf_bulk_ops.mixins", "BulkUpsertMixin"),
    "BulkUpsertView": ("drf_bulk_ops.views", "BulkUpsertView"),
    "DuplicateKeyError": ("drf_bulk_ops.exceptions", "DuplicateKeyError"),
    "GenericBulkAPIView": ("drf_bulk_ops.views", "GenericBulkAPIView"),
}


def __getattr__(name: str) -> Any:
    try:
        module_path, attr = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    from importlib import import_module

    value = getattr(import_module(module_path), attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(__all__))
