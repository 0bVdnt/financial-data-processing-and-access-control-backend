from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    """Pagination metadata included in list responses."""

    page: int
    per_page: int
    total: int
    total_pages: int


class ErrorDetail(BaseModel):
    """Structured error information"""

    code: str
    message: str
    fields: dict[str, str] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """
    Consistent response envelope used by all endpoints

    Success: {"success": true, "data": ..., "meta": ...}
    Error: {"success": false, "error": {"code": ..., "message": ...}}
    """

    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None
    meta: Meta | None = None
