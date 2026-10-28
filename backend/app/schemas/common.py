from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str

class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

class ErrorResponse(BaseModel):
    error: ErrorBody

class MessageResponse(BaseModel):
    message: str
