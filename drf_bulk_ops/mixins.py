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
    def schema_for_request(view_class, serializer_class, lookup_field):
        if not SPECTACULAR_INSTALLED:
            return view_class

        class BulkCreateDocumentSerializer(
            serializer_class,
        ):
            class Meta(serializer_class.Meta):
                fields = [
                    field
                    for field in getattr(serializer_class.Meta, "fields", [])
                    if field != lookup_field
                ]

        extended_view = extend_schema_view(
            post=extend_schema(request=BulkCreateDocumentSerializer(many=True)),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "serializer_class", None) and getattr(
            cls, "documentation", True
        ):
            cls.schema_for_request(cls, cls.serializer_class, cls.lookup_field)

    # ______API Documentation____

    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        instances = self.get_instances_for_create(serializer.validated_data)
        atomic = getattr(self, "atomic", True)

        bulk_operator = BulkCreateOperation(
            self.get_serializer_class(), batch_size=self.get_batch_size(), atomic=atomic
        )
        # Execution is handled inside the operation itself
        return bulk_operator.create(
            instances,
        )


class BulkUpdateMixin:

    # ______API Documentation____

    @staticmethod
    def schema_for_request(view_class, serializer_class, lookup_field):
        if not SPECTACULAR_INSTALLED:
            return view_class

        class BulkUpdateDocumentSerializer(serializer_class):
            class Meta(serializer_class.Meta):
                pass

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if lookup_field in self.fields:
                    self.fields[lookup_field].required = True

        extended_view = extend_schema_view(
            put=extend_schema(request=BulkUpdateDocumentSerializer(many=True)),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Pass lookup_field to schema generation
        if (
            getattr(cls, "serializer_class", None) is not None
            and getattr(cls, "lookup_field", None) is not None
        ):
            cls.schema_for_request(cls, cls.serializer_class, cls.lookup_field)

    # ______API Documentation____

    def bulk_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_update(serializer)
        return Response(status=status.HTTP_200_OK)

    def perform_bulk_update(self, serializer):
        data_list = serializer.validated_data
        queryset = self.get_queryset_for_update(data_list)
        atomic = getattr(self, "atomic", True)

        bulk_operator = BulkUpdateOperation(
            queryset=queryset,
            serializer=self.get_serializer_class(),
            lookup_field=self.lookup_field,
            batch_size=self.get_batch_size(),
            atomic=atomic,
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
        self.perform_bulk_destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self):
        queryset = self.get_queryset_for_destroy()
        # Retrieve atomic setting safely
        atomic = getattr(self, "atomic", True)

        bulk_operator = BulkDeleteOperation(queryset=queryset, atomic=atomic)
        return bulk_operator.delete()


class BulkUpsertMixin:

    # ______API Documentation____

    @staticmethod
    def schema_for_request(view_class, serializer_class, lookup_field):
        if not SPECTACULAR_INSTALLED:
            return view_class

        # Make lookup_field optional in the schema
        class BulkUpsertDocumentSerializer(serializer_class):
            class Meta(serializer_class.Meta):
                pass

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if lookup_field in self.fields:
                    self.fields[lookup_field].required = False

        extended_view = extend_schema_view(
            post=extend_schema(request=BulkUpsertDocumentSerializer(many=True)),
        )(view_class)
        return extended_view

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Pass lookup_field to schema generation
        if (
            getattr(cls, "serializer_class", None) is not None
            and getattr(cls, "lookup_field", None) is not None
        ):
            cls.schema_for_request(cls, cls.serializer_class, cls.lookup_field)

    # ______API Documentation____

    def bulk_upsert(self, request, *args, **kwargs):
        # Validate all incoming data
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_upsert(serializer)
        return Response(status=status.HTTP_200_OK)

    def perform_bulk_update(self, data_list):
        atomic = getattr(self, "atomic", True)
        queryset = self.get_queryset_for_update(data_list)
        bulk_update_operator = BulkUpdateOperation(
            queryset=queryset,
            serializer=self.get_serializer_class(),
            lookup_field=self.lookup_field,
            batch_size=self.get_batch_size(),
            atomic=atomic,
        )
        bulk_update_operator.update(data_list)

    def perform_bulk_create(self, data_list):
        atomic = getattr(self, "atomic", True)
        instances = self.get_instances_for_create(data_list)
        bulk_create_operator = BulkCreateOperation(
            self.get_serializer_class(), batch_size=self.get_batch_size(), atomic=atomic
        )
        bulk_create_operator.create(instances)

    def perform_bulk_upsert(self, serializer):
        data_list = serializer.validated_data

        # Separate data into items to create and items to update
        items_to_create = []
        items_to_update = []

        for item in data_list:
            if item.get(self.lookup_field):
                # Has a lookup field value, so it should be updated
                items_to_update.append(item)
            else:
                # No lookup field value, so it's a new instance to create
                items_to_create.append(item)

        # Perform create for new items
        if items_to_create:
            self.perform_bulk_create(items_to_create)

        # Perform update for existing items
        if items_to_update:
            self.perform_bulk_update(items_to_update)
