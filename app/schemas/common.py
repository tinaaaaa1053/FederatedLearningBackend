"""
Common response schemas
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format"""
    records: List[T]
    total: int
    pageNo: int
    pageSize: int


class PaginationRequest(BaseModel):
    """Common pagination request"""
    pageNo: int = 1
    pageSize: int = 10
