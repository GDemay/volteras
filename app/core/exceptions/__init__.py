# Initialize the exceptions module
from .http_exceptions import HTTPException, ResourceNotFoundException

__all__ = [
    "HTTPException",
    "ResourceNotFoundException",
]
