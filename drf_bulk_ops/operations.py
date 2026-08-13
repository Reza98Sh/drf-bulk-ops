from django.db import transaction

class BaseBulkOperation:
    def __init__(self, atomic, batch_size=None):
        self.atomic = atomic
        self.batch_size = batch_size

    def execute(self, *args, **kwargs):
        # Wrap execution in transaction if atomic is enabled
        if self.atomic:
            with transaction.atomic():
                return self._run(*args, **kwargs)
        return self._run(*args, **kwargs)

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement _run method.")


class BulkCreateOperation(BaseBulkOperation):
    def __init__(self,  serializer, atomic, batch_size=None):
        super().__init__(atomic=atomic, batch_size=batch_size)
        self.serializer = serializer

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def _run(self, instances):
        return self.model_class.objects.bulk_create(
            instances, batch_size=self.batch_size
        )
        
    def create(self, instances):
        return self.execute(instances)


class BulkUpdateOperation(BaseBulkOperation):
    def __init__(self, queryset, serializer, lookup_field, atomic, batch_size=None):
        super().__init__(atomic=atomic, batch_size=batch_size)
        self.queryset = queryset
        self.serializer = serializer
        self.lookup_field = lookup_field

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def get_update_fields(self):
        # We need self.serializer to extract writable fields
        model = self.model_class
        model_field_names = {
            field.name for field in model._meta.concrete_fields
        }
        
        writable_fields = []
        for name, field in self.serializer().fields.items():
            # Skip read-only fields
            if field.read_only:
                continue
                
            # Exclude the lookup field from the update list
            if name in model_field_names and name != self.lookup_field:
                writable_fields.append(name)

        return writable_fields


    def _run(self, data_list):
        update_fields = self.get_update_fields()
        qs = self.queryset.only(self.lookup_field, *update_fields)
        instances = {getattr(obj, self.lookup_field): obj for obj in qs}

        updated_instances = []
        for item in data_list:
            obj_id = item.get(self.lookup_field)
            obj = instances.get(obj_id)

            if not obj:
                continue

            for key, value in item.items():
                if key != self.lookup_field:
                    setattr(obj, key, value)

            updated_instances.append(obj)

        self.model_class.objects.bulk_update(
            updated_instances, update_fields, batch_size=self.batch_size
        )
        return updated_instances

    # Override public method to pass data_list to _run
    def update(self, data_list):
        return self.execute(data_list)


class BulkDeleteOperation(BaseBulkOperation):
    def __init__(self, queryset, atomic):
        super().__init__(atomic=atomic)
        self.queryset = queryset

    def _run(self):
        return self.queryset.delete()

    # Override public method to match original interface
    def delete(self):
        return self.execute()
