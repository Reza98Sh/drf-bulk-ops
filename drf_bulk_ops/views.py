from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError
from drf_bulk_ops import mixins

class GenericBulkAPIView(GenericAPIView):
    """
    Base API View for bulk operations.
    Provides hooks for developers to extend and customize bulk behaviors.
    """
    batch_size = 1000
    lookup_field = "id"

    def get_batch_size(self):
        return self.batch_size

    def get_instances_for_create(self, data_list):
        model_class = self.get_serializer_class().Meta.model
        try:
            return [model_class(**item) for item in data_list]
        except TypeError as exc:
            raise ValidationError(f"Invalid data for {model_class.__name__}: {exc}")

    def get_queryset_for_destroy(self, data_list):
        key = f"{self.lookup_field}s"
        identifiers = data_list.get(key, [])

        if not identifiers:
            raise ValidationError({key: f"No {key} provided for deletion."})

        return self.get_queryset().filter(**{f"{self.lookup_field}__in": identifiers})

    def get_queryset_for_update(self, data_list):
        unique_values = [
            item[self.lookup_field] for item in data_list if item.get(self.lookup_field)
        ]

        if not unique_values:
            raise ValidationError(f"No {self.lookup_field}s provided for update.")

        return self.get_queryset().filter(**{f"{self.lookup_field}__in": unique_values})


class BulkCreateView(mixins.BulkCreateMixin, GenericBulkAPIView):
    def post(self, request, *args, **kwargs):
        return self.bulk_create(request, *args, **kwargs)


class BulkUpdateView(mixins.BulkUpdateMixin, GenericBulkAPIView):
    def put(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)


class BulkDestroyView(mixins.BulkDestroyMixin, GenericBulkAPIView):
    def delete(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)


class BulkCreateDestroyView(mixins.BulkDestroyMixin, mixins.BulkCreateMixin, GenericBulkAPIView):
    def post(self, request, *args, **kwargs):
        return self.bulk_create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)
