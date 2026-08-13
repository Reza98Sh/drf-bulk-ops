class BulkOpsSerializerMixin:
    """
    Mixin that makes the lookup field writable so it can be
    submitted in bulk update/upsert payloads.
    Dynamically handles the requirement of the lookup_field based on the
    view's operation type (Create, Update, Upsert)
    """

    def get_fields(self):
        fields = super().get_fields()

        view = self.context.get("view")
        request = self.context.get("request")

        lookup_field = getattr(view, "lookup_field", "id")

        if lookup_field in fields:
            target_field = fields[lookup_field]

            # Make the field writable so it can be accepted in incoming payloads
            target_field.read_only = False

            is_required = False

            if view and request:
                # Check the capabilities of the view to deduce the operation
                is_upsert = hasattr(view, "bulk_upsert")
                is_update = hasattr(view, "bulk_update")

                if is_upsert:
                    # For upsert operations, lookup_field is optional
                    is_required = False
                elif is_update:
                    # For strict update operations, lookup_field is mandatory
                    is_required = True
                else:
                    # For create (POST) or any other operations, it is not mandatory
                    is_required = False

            target_field.required = is_required

        return fields
