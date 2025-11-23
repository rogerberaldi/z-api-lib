"""Exception classes for zapi_async."""

from __future__ import annotations
from typing import Any


class ZAPIError(Exception):
    """Base exception for all Z-API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ZAPIError):
    """Raised when authentication fails (invalid instance ID, token, or client token)."""
    pass


class InstanceError(ZAPIError):
    """Raised when instance is not connected or unavailable."""
    pass


class RateLimitError(ZAPIError):
    """Raised when rate limit is exceeded."""
    pass


class MessageError(ZAPIError):
    """Raised when message sending fails."""
    pass


class WebhookError(ZAPIError):
    """Raised when webhook configuration fails."""
    pass


class ValidationError(ZAPIError):
    """Raised when request validation fails."""
    pass


class MediaError(ZAPIError):
    """Raised when media upload or processing fails."""
    pass


class GroupError(ZAPIError):
    """Raised when group operations fail."""
    pass


class NetworkError(ZAPIError):
    """Raised when network/connection errors occur."""
    pass
