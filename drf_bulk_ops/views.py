from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError

from . import mixins
from .queries import BulkQuery
from .serializer import BulkOpsSerializerMixin

class GenericBulkAPIView(GenericAPIView):
    """
    Base API View for bulk operations.
    Provides hooks for developers to extend and customize bulk behaviors.
    """

    batch_size = 500
    lookup_field = "id"
    documentation = True
    atomic = True
    
    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        # Verify if the serializer class inherits from BulkOpsSerializerMixin
        if not issubclass(serializer_class, BulkOpsSerializerMixin):
            raise TypeError(
                f"Serializer class {serializer_class.__name__} must inherit from BulkOpsSerializerMixin"
            )
        return serializer_class

    def get_batch_size(self):
        return self.batch_size

    def get_query(self):
        return BulkQuery(atomic=self.atomic, batch_size=self.get_batch_size())

    def get_instances_for_create(self, data_list):
        model_class = self.get_serializer_class().Meta.model
        try:
            return [model_class(**item) for item in data_list]
        except TypeError as exc:
            raise ValidationError(f"Invalid data for {model_class.__name__}: {exc}")

    def get_queryset_for_destroy(self):
        key = f"{self.lookup_field}s"

        raw_identifiers = self.request.query_params.getlist(key)

        identifiers = []
        for item in raw_identifiers:
            # Handle comma-separated values like ?ids=1,2,3
            identifiers.extend([i.strip() for i in item.split(",") if i.strip()])

        if not identifiers:
            raise ValidationError(
                {key: f"No {key} provided in query parameters for deletion."}
            )

        return self.get_queryset().filter(**{f"{self.lookup_field}__in": identifiers})

    def get_queryset_for_update(self, data_list):
        unique_values = [
            item[self.lookup_field] for item in data_list if item.get(self.lookup_field)
        ]

        if not unique_values:
            raise ValidationError(f"No {self.lookup_field}s provided for update.")

        return self.get_queryset().filter(**{f"{self.lookup_field}__in": unique_values})


class BulkCreateView(
    mixins.BulkCreateMixin,
    GenericBulkAPIView,
):
    def post(self, request, *args, **kwargs):
        return self.bulk_create(request, *args, **kwargs)


class BulkUpdateView(mixins.BulkUpdateMixin, GenericBulkAPIView):
    def put(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)


class BulkDestroyView(mixins.BulkDestroyMixin, GenericBulkAPIView):
    def delete(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)


class BulkCreateDestroyView(
    mixins.BulkDestroyMixin, mixins.BulkCreateMixin, GenericBulkAPIView
):
    def post(self, request, *args, **kwargs):
        return self.bulk_create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)

class BulkUpsertView(mixins.BulkUpsertMixin, GenericBulkAPIView):
    
    def post(self, request, *args, **kwargs):
        return self.bulk_upsert(request, *args, **kwargs)