from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from drf_bulk_ops.operations import (
    BulkCreateOperation,
    BulkUpdateOperation,
    BulkDeleteOperation,
)

try:
    from drf_spectacular.utils import (
        OpenApiParameter,
        extend_schema,
        extend_schema_view,
    )
    from drf_spectacular.types import OpenApiTypes

    SPECTACULAR_INSTALLED = True
except ImportError:
    SPECTACULAR_INSTALLED = False


class BulkCreateMixin:

    # ______API Documentation____

    @staticmethod
    def schema_for_request(view_class, serializer_class):
        if not SPECTACULAR_INSTALLED:
            return view_class

        extended_view = extend_schema_view(
            post=extend_schema(request=serializer_class(many=True)),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "serializer_class", None) is not None:
            cls.schema_for_request(cls, cls.serializer_class)

    # ______API Documentation____

    def bulk_create(self, request, *args, **kwargs):
        # Always use get_serializer to allow context passing and overrides
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        is_atomic = getattr(self, 'get_atomic', lambda: False)()
        if is_atomic:
            # Wrap the operation in a database transaction
            with transaction.atomic():
                self.perform_bulk_create(serializer)
        else:
            self.perform_bulk_create(serializer)

        return Response(status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        instances = self.get_instances_for_create(serializer.validated_data)
        bulk_operator = BulkCreateOperation(
            instances, self.get_serializer_class(), batch_size=self.get_batch_size()
        )
        return bulk_operator.create()


class BulkUpdateMixin:

    # ______API Documentation____

    @staticmethod
    def schema_for_request(view_class, serializer_class):
        if not SPECTACULAR_INSTALLED:
            return view_class

        extended_view = extend_schema_view(
            put=extend_schema(request=serializer_class(many=True)),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "serializer_class", None) is not None:
            cls.schema_for_request(cls, cls.serializer_class)

    # ______API Documentation____

    def bulk_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        is_atomic = getattr(self, 'get_atomic', lambda: False)()
        if is_atomic:
            # Wrap the operation in a database transaction
            with transaction.atomic():
                self.perform_bulk_update(serializer)
        else:
            self.perform_bulk_update(serializer)

        return Response(status=status.HTTP_200_OK)

    def perform_bulk_update(self, serializer):
        data_list = serializer.validated_data
        queryset = self.get_queryset_for_update(data_list)
        bulk_operator = BulkUpdateOperation(
            queryset=queryset,
            serializer=self.get_serializer_class(),
            lookup_field=self.lookup_field,
            batch_size=self.get_batch_size(),
        )
        return bulk_operator.update(data_list)


class BulkDestroyMixin:

    # ______API Documentation____

    @staticmethod
    def schema_for_request(view_class, lookup_field):
        if not SPECTACULAR_INSTALLED:
            return view_class

        param = OpenApiParameter(
            name=lookup_field + "s",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description=f"Comma-separated list of {lookup_field}s to delete.",
        )

        extended_view = extend_schema_view(
            delete=extend_schema(parameters=[param]),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "lookup_field", None) is not None:
            cls.schema_for_request(cls, cls.lookup_field)

    # ______API Documentation____

    def bulk_destroy(self, request, *args, **kwargs):
        is_atomic = getattr(self, 'get_atomic', lambda: False)()
        if is_atomic:
            # Wrap the operation in a database transaction
            with transaction.atomic():
                self.perform_bulk_destroy()
        else:
            self.perform_bulk_destroy()
            
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self):
        queryset = self.get_queryset_for_destroy()
        bulk_operator = BulkDeleteOperation(
            queryset=queryset,
        )
        return bulk_operator.delete()
