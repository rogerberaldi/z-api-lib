"""Instance status and connection types."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class InstanceStatus:
    """
    Instance connection status.
    
    Attributes:
        connected: Whether instance is connected
        status: Connection status string
        phone: Connected phone number (if connected)
    """
    connected: bool
    status: str
    phone: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstanceStatus:
        """Create from API response."""
        return cls(
            connected=data.get('connected', False),
            status=data.get('status', 'unknown'),
            phone=data.get('phone')
        )


@dataclass
class QRCode:
    """
    QR Code for instance connection.
    
    Attributes:
        value: QR code value/bytes
        image: Base64 encoded QR code image (if available)
    """
    value: str
    image: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QRCode:
        """Create from API response."""
        # Response can be just the value string or dict
        if isinstance(data, str):
            return cls(value=data)
        return cls(
            value=data.get('value', data.get('qrcode', '')),
            image=data.get('image')
        )


@dataclass
class PhoneCode:
    """
    Phone code for connection without QR code.
    
    Attributes:
        code: Connection code
        phone: Phone number
    """
    code: str
    phone: str
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhoneCode:
        """Create from API response."""
        return cls(
            code=data.get('code', ''),
            phone=data.get('phone', '')
        )
