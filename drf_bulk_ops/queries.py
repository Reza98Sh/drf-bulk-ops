from django.db import transaction


class BaseQuery:
    def execute(self, batch_size=None):
        raise NotImplementedError("Subclasses must implement execute.")


class CreateQuery(BaseQuery):
    def __init__(self, model_class, instances):
        self.model_class = model_class
        self.instances = instances

    def execute(self, batch_size=None):
        return self.model_class.objects.bulk_create(
            self.instances, batch_size=batch_size
        )


class UpdateQuery(BaseQuery):
    def __init__(self, model_class, queryset, lookup_field, update_fields, data_list):
        self.model_class = model_class
        self.queryset = queryset
        self.lookup_field = lookup_field
        self.update_fields = update_fields
        self.data_list = data_list

    def execute(self, batch_size=None):
        qs = self.queryset.only(self.lookup_field, *self.update_fields)
        instances = {getattr(obj, self.lookup_field): obj for obj in qs}

        updated_instances = []
        for item in self.data_list:
            obj_id = item.get(self.lookup_field)
            obj = instances.get(obj_id)

            if not obj:
                continue

            for key, value in item.items():
                if key != self.lookup_field:
                    setattr(obj, key, value)

            updated_instances.append(obj)

        self.model_class.objects.bulk_update(
            updated_instances, self.update_fields, batch_size=batch_size
        )
        return updated_instances


class DeleteQuery(BaseQuery):
    def __init__(self, queryset):
        self.queryset = queryset

    def execute(self, batch_size=None):
        return self.queryset.delete()


class BulkQuery:
    """Runs one or more built queries with a shared atomic/batch_size policy."""

    def __init__(self, atomic=True, batch_size=None):
        self.atomic = atomic
        self.batch_size = batch_size

    def execute(self, *queries):
        if self.atomic:
            with transaction.atomic():
                return self._run(queries)
        return self._run(queries)

    def _run(self, queries):
        return [query.execute(batch_size=self.batch_size) for query in queries]
