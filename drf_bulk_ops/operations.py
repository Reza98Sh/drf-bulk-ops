from .queries import CreateQuery, DeleteQuery, UpdateQuery


class BulkCreateOperation:
    def __init__(self, serializer):
        self.serializer = serializer

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def build(self, instances):
        return CreateQuery(self.model_class, instances)


class BulkUpdateOperation:
    def __init__(self, queryset, serializer, lookup_field):
        self.queryset = queryset
        self.serializer = serializer
        self.lookup_field = lookup_field

    @property
    def model_class(self):
        return self.serializer.Meta.model

    def get_update_fields(self):
        model = self.model_class
        model_field_names = {
            field.name for field in model._meta.concrete_fields
        }

        writable_fields = []
        for name, field in self.serializer().fields.items():
            if field.read_only:
                continue

            if name in model_field_names and name != self.lookup_field:
                writable_fields.append(name)

        return writable_fields

    def build(self, data_list):
        return UpdateQuery(
            model_class=self.model_class,
            queryset=self.queryset,
            lookup_field=self.lookup_field,
            update_fields=self.get_update_fields(),
            data_list=data_list,
        )


class BulkDeleteOperation:
    def __init__(self, queryset):
        self.queryset = queryset

    def build(self):
        return DeleteQuery(self.queryset)
