"""
Custom exceptions for bulk operations.

These exceptions provide domain-specific error handling for bulk operations,
with structured error information for better API responses.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class BulkOperationError(APIException):
    """Base exception for all bulk operation errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A bulk operation error occurred."
    default_code = "bulk_operation_error"


class DuplicateKeyError(BulkOperationError):
    """
    Raised when duplicate unique_field combinations found in request.

    Attributes:
        duplicates: List of duplicate unique_field combinations
    """

    default_detail = "Duplicate unique field combinations found in request."
    default_code = "duplicate_key"

    def __init__(self, duplicates, detail=None, code=None):
        """
        Initialize with list of duplicates.

        Args:
            duplicates: List of dicts containing duplicate unique field values
            detail: Optional custom error message
            code: Optional custom error code
        """
        self.duplicates = duplicates
        if detail is None:
            detail = f"{self.default_detail} Found {len(duplicates)} duplicate(s)."
        super().__init__(detail, code)

