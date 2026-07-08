from rest_framework.response import Response
from rest_framework import status
from drf_bulk_ops.operations import (
    BulkCreateOperation,
    BulkUpdateOperation,
    BulkDeleteOperation,
)

class BulkCreateMixin:
    def bulk_create(self, request, *args, **kwargs):
        # Always use get_serializer to allow context passing and overrides
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        created_instances = self.perform_bulk_create(serializer)
        output_serializer = self.get_serializer(created_instances, many=True)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        instances = self.get_instances_for_create(serializer.validated_data)
        bulk_operator = BulkCreateOperation(
            instances, self.get_serializer_class(), batch_size=self.get_batch_size()
        )
        return bulk_operator.create()


class BulkUpdateMixin:
    def bulk_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        updated_instances = self.perform_bulk_update(serializer)
        output_serializer = self.get_serializer(updated_instances, many=True)
        # Added the missing return statement
        return Response(output_serializer.data, status=status.HTTP_200_OK)

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
    def bulk_destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_bulk_destroy(serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_bulk_destroy(self, serializer):
        data_list = serializer.validated_data
        queryset = self.get_queryset_for_destroy(self.request.data)
        bulk_operator = BulkDeleteOperation(
            queryset=queryset,
        )
        return bulk_operator.delete()
