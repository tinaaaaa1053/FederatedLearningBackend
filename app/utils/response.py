"""
Response formatting utilities
"""
from typing import Any, Optional
from app.schemas.common import ApiResponse


def success_response(data: Any = None, message: str = "success") -> ApiResponse:
    """Create a success response"""
    return ApiResponse(code=200, message=message, data=data)


def error_response(
    message: str,
    code: int = 500,
    data: Optional[Any] = None
) -> ApiResponse:
    """Create an error response"""
    return ApiResponse(code=code, message=message, data=data)
