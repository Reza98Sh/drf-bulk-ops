class BulkCreateOperation:
    def __init__(self, instances, serializer, batch_size=None):
        self.instances = instances
        self.serializer = serializer
        self.batch_size = batch_size

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def create(self):
        return self.model_class.objects.bulk_create(
            self.instances, batch_size=self.batch_size
        )


class BulkUpdateOperation:
    def __init__(self, queryset, serializer, lookup_field="id", batch_size=None):
        self.queryset = queryset
        self.serializer = serializer
        self.batch_size = batch_size
        self.lookup_field = lookup_field

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def get_update_fields(self, serializer):
        model = self.model_class
        model_field_names = {
            field.name for field in model._meta.concrete_fields
        }

        writable_fields = []
        for name, field in serializer().fields.items():
            if field.read_only:
                continue
            if name in {model._meta.pk.name, "pk", self.lookup_field}:
                continue
            if name in model_field_names:
                writable_fields.append(name)

        return writable_fields

    def update(self, data_list):
        update_fields = self.get_update_fields()
        
        # Optimize query but ensure we only map fields we need
        qs = self.queryset.only(self.lookup_field, *update_fields)
        
        # Fixed: Use self.lookup_field dynamically instead of hardcoding .id
        instances = {getattr(obj, self.lookup_field): obj for obj in qs}

        updated_instances = []

        for item in data_list:
            # Fixed: Use lookup_field instead of hardcoded 'id'
            obj_id = item.get(self.lookup_field)
            obj = instances.get(obj_id)

            if not obj:
                continue

            for key, value in item.items():
                if key != self.lookup_field:
                    # Fixed: Use setattr to properly trigger Django field descriptors
                    setattr(obj, key, value)

            updated_instances.append(obj)

        self.model_class.objects.bulk_update(
            updated_instances, update_fields, batch_size=self.batch_size
        )
        return updated_instances


class BulkDeleteOperation:
    def __init__(self, queryset):
        self.queryset = queryset

    def delete(self):
        # Note: queryset.delete() doesn't naturally support batch_size in Django. 
        # If batching is strictly required for memory limits on huge deletes, 
        # you might need to slice and loop, otherwise this ignores batch_size.
        return self.queryset.delete()
